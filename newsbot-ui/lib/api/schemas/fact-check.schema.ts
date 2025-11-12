import { z } from "zod";

/**
 * Fact check request schema
 */
export const FactCheckRequestSchema = z.object({
  article_id: z.string(),
  headline: z.string(),
  summary: z.string(),
  source: z.string(),
});

export type FactCheckRequest = z.infer<typeof FactCheckRequestSchema>;

/**
 * Source comparison schema
 */
export const SourceComparisonSchema = z.object({
  source: z.string(),
  article_id: z.string(),
  headline: z.string(),
  summary: z.string(),
  trust_score: z.number(),
  credibility: z.string(), // "high", "medium", "low"
  fact_accuracy: z.number(),
  bias_level: z.string(), // "low", "medium", "high"
  reasoning: z.string(),
});

export type SourceComparison = z.infer<typeof SourceComparisonSchema>;

/**
 * Fact check response schema
 */
export const FactCheckResponseSchema = z.object({
  original_article_id: z.string(),
  original_source: z.string(),
  original_headline: z.string(),
  comparisons: z.array(SourceComparisonSchema),
  overall_assessment: z.string(),
  recommendation: z.string(),
  total_sources_found: z.number(),
});

export type FactCheckResponse = z.infer<typeof FactCheckResponseSchema>;
