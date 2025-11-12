import logging
from typing import Dict, List

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.models.embedding_model import get_embedding_model
from app.core.qdrant import get_collection_name, get_qdrant_client
from app.services.article.article_service import ArticleService
from app.services.llm.llm_client import LLMClient

logger = logging.getLogger(__name__)


class FactCheckService:
    """Service for fact-checking articles by comparing with similar sources."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.article_service = ArticleService(db)
        self.llm_client = LLMClient()
        self.llm = self.llm_client.llm  # Get the underlying OllamaLLM
        self.qdrant_client = get_qdrant_client()
        self.collection_name = get_collection_name()
        self.embedding_model = get_embedding_model()

    async def fact_check_article(
        self,
        article_id: str,
        headline: str,
        summary: str,
        source: str,
        k: int = 5,
    ) -> Dict:
        """
        Fact-check an article by finding similar articles from different sources
        and performing LLM-based comparative analysis.

        Args:
            article_id: The ID of the article to fact-check
            headline: The headline of the article
            summary: The summary/content of the article
            source: The original source name
            k: Number of similar articles to retrieve for final fact-checking

        Returns:
            Dict containing fact-check results with source comparisons
        """
        try:
            # Step 1: Generate embedding for the headline
            import asyncio

            logger.info(f"Starting fact-check for article: {article_id}")
            logger.info(f"Headline: {headline}")

            title_embedding = await asyncio.to_thread(
                self.embedding_model.encode, headline
            )

            logger.info(
                f"Generated title embedding with shape: {title_embedding.shape}"
            )

            # Step 2: Search Qdrant for similar articles using title_embedding
            # Get 15 candidates to allow LLM to filter
            logger.info("Searching Qdrant for similar articles...")
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=("title_embedding", title_embedding.tolist()),
                limit=15,
                with_payload=True,
            )
            logger.info(f"Found {len(search_results)} similar articles from Qdrant")

            # Step 3: Build candidate list for LLM filtering
            candidates = []
            for result in search_results:
                payload = result.payload
                candidate_article_id = payload.get("article_id", "")
                candidate_source = payload.get("source_name", "")

                # Skip the same article
                if candidate_article_id == article_id:
                    continue

                candidates.append(
                    {
                        "article_id": candidate_article_id,
                        "title": payload.get("title", ""),
                        "source": candidate_source,
                        "score": result.score,
                    }
                )

            if not candidates:
                logger.warning(
                    "No candidate articles found after filtering same article"
                )
                return {
                    "original_article_id": article_id,
                    "original_source": source,
                    "original_headline": headline,
                    "comparisons": [],
                    "overall_assessment": "No similar articles were found in the database.",
                    "recommendation": "Cannot perform fact-checking without comparative sources.",
                    "total_sources_found": 0,
                }

            # Step 4: Ask LLM to determine which articles are about the same story
            # from different sources
            logger.info(f"Filtering {len(candidates)} candidates with LLM...")
            filtered_candidates = await self._filter_similar_articles_with_llm(
                original_headline=headline,
                original_source=source,
                candidates=candidates,
                max_results=k,
            )
            logger.info(f"LLM filtered to {len(filtered_candidates)} relevant articles")

            if not filtered_candidates:
                logger.warning(
                    "No articles covering the same story from different sources found"
                )
                return {
                    "original_article_id": article_id,
                    "original_source": source,
                    "original_headline": headline,
                    "comparisons": [],
                    "overall_assessment": "No articles covering the same story from different sources were found.",
                    "recommendation": "Cannot perform fact-checking without comparative sources.",
                    "total_sources_found": 0,
                }

            # Step 5: Fetch full article details from MongoDB for filtered candidates
            article_ids = [c["article_id"] for c in filtered_candidates]
            logger.info(
                f"Fetching full details for {len(article_ids)} articles from MongoDB"
            )
            articles = await self.article_service.get_articles_by_ids(article_ids)
            logger.info(f"Retrieved {len(articles)} articles from MongoDB")

            # Create a mapping for quick lookup
            articles_map = {a.article_id: a for a in articles}

            # Step 6: Perform LLM-based comparative analysis for each filtered article
            logger.info("Starting comparative analysis...")
            comparisons = []
            for candidate in filtered_candidates:
                candidate_id = candidate["article_id"]
                if candidate_id not in articles_map:
                    continue

                article = articles_map[candidate_id]
                comparison = await self._analyze_source_comparison(
                    original_headline=headline,
                    original_summary=summary,
                    original_source=source,
                    comparison_headline=article.title,
                    comparison_summary=article.summary or "",
                    comparison_source=article.source_name,
                    comparison_article_id=candidate_id,
                )
                if comparison:
                    comparisons.append(comparison)

            logger.info(f"Completed {len(comparisons)} comparative analyses")

            # Step 7: Generate overall assessment
            overall_assessment = await self._generate_overall_assessment(
                headline=headline,
                summary=summary,
                source=source,
                comparisons=comparisons,
            )

            return {
                "original_article_id": article_id,
                "original_source": source,
                "original_headline": headline,
                "comparisons": comparisons,
                "overall_assessment": overall_assessment["assessment"],
                "recommendation": overall_assessment["recommendation"],
                "total_sources_found": len(comparisons),
            }

        except Exception as e:
            logger.error(f"Error in fact_check_article: {str(e)}")
            raise

    async def _filter_similar_articles_with_llm(
        self,
        original_headline: str,
        original_source: str,
        candidates: List[Dict],
        max_results: int = 5,
    ) -> List[Dict]:
        """
        Use LLM to determine which candidate articles are about the same story
        from different sources.

        Args:
            original_headline: The original article headline
            original_source: The original article source
            candidates: List of candidate articles with title, source, article_id
            max_results: Maximum number of results to return

        Returns:
            List of filtered candidate dictionaries
        """
        try:
            # Build candidate list for LLM
            candidates_text = "\n".join(
                [
                    f"{i+1}. [{c['source']}] {c['title']} (ID: {c['article_id']})"
                    for i, c in enumerate(candidates)
                ]
            )

            logger.info(f"Asking LLM to filter {len(candidates)} candidates")
            logger.debug(f"Candidates:\n{candidates_text}")

            prompt = f"""You are a fact-checking assistant. Your task is to identify which of the following \
articles are covering the SAME story as the original article, but published by DIFFERENT sources.

ORIGINAL ARTICLE:
Source: {original_source}
Headline: {original_headline}

CANDIDATE ARTICLES:
{candidates_text}

Analyze each candidate and determine if it's:
1. About the SAME story/event/topic as the original article
2. From a DIFFERENT news source (not {original_source})

Return ONLY the IDs of articles that match BOTH criteria, separated by commas.
If none match, return "NONE".
Maximum {max_results} articles.

Example response: article-123, article-456, article-789
Or: NONE

Your response:"""

            response = await self.llm._acall(prompt)
            response = response.strip()

            logger.info(f"LLM response for filtering: {response}")

            # Parse the response
            if response.upper() == "NONE" or not response:
                logger.info("LLM returned NONE or empty response")
                return []

            # Extract article IDs from response
            selected_ids = set()
            for part in response.split(","):
                part = part.strip()
                # Try to find article_id in the part
                for candidate in candidates:
                    if candidate["article_id"] in part:
                        selected_ids.add(candidate["article_id"])

            # Filter candidates to only selected ones
            filtered = [c for c in candidates if c["article_id"] in selected_ids]

            # Limit to max_results
            logger.info(
                f"Filtered {len(filtered)} articles from {len(selected_ids)} IDs"
            )
            return filtered[:max_results]

        except Exception as e:
            logger.error(f"Error in _filter_similar_articles_with_llm: {str(e)}")
            # Fallback: return candidates from different sources
            fallback = [
                c for c in candidates if c["source"].lower() != original_source.lower()
            ][:max_results]
            logger.info(f"Using fallback filtering, returning {len(fallback)} articles")
            return fallback

    async def _analyze_source_comparison(
        self,
        original_headline: str,
        original_summary: str,
        original_source: str,
        comparison_headline: str,
        comparison_summary: str,
        comparison_source: str,
        comparison_article_id: str,
    ) -> Dict:
        """
        Use LLM to analyze and compare two articles from different sources.
        """
        try:
            prompt = f"""You are a fact-checking expert. Compare these two articles covering the same story:

ORIGINAL ARTICLE:
Source: {original_source}
Headline: {original_headline}
Summary: {original_summary}

COMPARISON ARTICLE:
Source: {comparison_source}
Headline: {comparison_headline}
Summary: {comparison_summary}

Analyze the comparison article and provide:
1. Trust Score (0-100): Overall reliability score
2. Credibility (high/medium/low): Source credibility level
3. Fact Accuracy (0-100): How accurate the facts are
4. Bias Level (low/medium/high): Detected bias in reporting
5. Reasoning: Brief explanation (2-3 sentences) of your analysis

Respond in this EXACT format:
TRUST_SCORE: [number]
CREDIBILITY: [high/medium/low]
FACT_ACCURACY: [number]
BIAS_LEVEL: [low/medium/high]
REASONING: [your explanation]"""

            # Get LLM response
            response = await self.llm._acall(prompt)

            # Parse the response
            lines = response.strip().split("\n")
            result = {
                "source": comparison_source,
                "article_id": comparison_article_id,
                "headline": comparison_headline,
                "summary": comparison_summary,
                "trust_score": 70,  # default
                "credibility": "medium",  # default
                "fact_accuracy": 70,  # default
                "bias_level": "medium",  # default
                "reasoning": "Unable to parse LLM response",
            }

            for line in lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip().lower()
                    value = value.strip()

                    if "trust_score" in key or "trust score" in key:
                        try:
                            result["trust_score"] = int(value)
                        except ValueError:
                            pass
                    elif "credibility" in key:
                        result["credibility"] = value.lower()
                    elif "fact_accuracy" in key or "fact accuracy" in key:
                        try:
                            result["fact_accuracy"] = int(value)
                        except ValueError:
                            pass
                    elif "bias_level" in key or "bias level" in key:
                        result["bias_level"] = value.lower()
                    elif "reasoning" in key:
                        result["reasoning"] = value

            return result

        except Exception as e:
            logger.error(f"Error in _analyze_source_comparison: {str(e)}")
            return None

    async def _generate_overall_assessment(
        self,
        headline: str,
        summary: str,
        source: str,
        comparisons: List[Dict],
    ) -> Dict:
        """
        Generate an overall assessment based on all source comparisons.
        """
        try:
            if not comparisons:
                return {
                    "assessment": "No comparative sources available for analysis.",
                    "recommendation": "Cannot provide recommendation without comparative data.",
                }

            # Build comparison summary
            comparison_summary = "\n".join(
                [
                    f"- {c['source']}: Trust {c['trust_score']}/100, "
                    f"Credibility: {c['credibility']}, "
                    f"Bias: {c['bias_level']}"
                    for c in comparisons
                ]
            )

            prompt = f"""You are a fact-checking expert. Based on the analysis of multiple sources covering the same story, provide an overall assessment.

ORIGINAL ARTICLE:
Source: {source}
Headline: {headline}
Summary: {summary}

COMPARATIVE SOURCES ANALYSIS:
{comparison_summary}

Provide:
1. Overall Assessment: A 2-3 sentence summary of how reliable this story is across sources
2. Recommendation: A brief recommendation for readers (1-2 sentences)

Respond in this EXACT format:
ASSESSMENT: [your assessment]
RECOMMENDATION: [your recommendation]"""

            response = await self.llm._acall(prompt)

            # Parse response
            lines = response.strip().split("\n")
            result = {
                "assessment": "Multiple sources confirm the core facts of this story.",
                "recommendation": "This article appears reliable based on cross-source verification.",
            }

            for line in lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip().lower()
                    value = value.strip()

                    if "assessment" in key:
                        result["assessment"] = value
                    elif "recommendation" in key:
                        result["recommendation"] = value

            return result

        except Exception as e:
            logger.error(f"Error in _generate_overall_assessment: {str(e)}")
            return {
                "assessment": "Error generating assessment.",
                "recommendation": "Unable to provide recommendation at this time.",
            }
