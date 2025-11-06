from __future__ import annotations

import json
import logging
from typing import Any, List, Mapping, Optional

import httpx
import requests
from langchain.llms.base import LLM

from app.core.config import settings

logger = logging.getLogger(__name__)


class OllamaLLM(LLM):
    """
    Minimal Ollama LLM wrapper for LangChain.

    Note: The Ollama HTTP API can differ between versions. This wrapper
    posts a JSON payload to `{base_url}/api/generate` by default.
    Adjust endpoint/payload parsing to match your Ollama server if needed.
    """

    base_url: str
    model_name: str
    temperature: float = 0.3
    max_tokens: Optional[int] = None
    stop: Optional[List[str]] = None

    def __init__(
        self,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None,
    ):
        # Resolve defaults from settings first, then pass to pydantic-backed
        # BaseModel initializer. Calling super().__init__ ensures pydantic
        # internal attributes like __fields_set__ are created and avoids
        # AttributeError when assigning attributes directly.
        resolved_base = base_url or settings.llm_base_url
        resolved_model = model_name or settings.llm_model
        # Use super().__init__ to let pydantic set up the model correctly
        super().__init__(
            base_url=resolved_base,
            model_name=resolved_model,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
        )

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {
            "base_url": self.base_url,
            "model_name": self.model_name,
            "temperature": self.temperature,
        }

    @property
    def _llm_type(self) -> str:
        return "ollama"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """
        Synchronous call to Ollama REST API. Adjust endpoint/payload per your server version.
        """
        logger.info(f"🤖 Calling Ollama LLM with model: {self.model_name}")
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "temperature": self.temperature,
        }
        if self.max_tokens:
            payload["max_tokens"] = self.max_tokens
        if stop:
            payload["stop"] = stop
        url = f"{self.base_url.rstrip('/')}/api/generate"

        # Ollama may stream NDJSON lines (one JSON object per line) with
        # incremental 'response' fields. To handle both streaming and
        # non-streaming responses, request the endpoint with stream=True and
        # accumulate any returned chunks.
        # Increased timeout to 300s (5min) to allow model loading on first request
        logger.debug(
            "⏳ Waiting for Ollama response (may take up to 5min on first load)..."
        )
        chunks: List[str] = []
        with requests.post(url, json=payload, timeout=300, stream=True) as resp:
            resp.raise_for_status()

            # Iterate over streamed lines. For non-streaming responses this
            # will typically yield the full JSON once.
            for line in resp.iter_lines(decode_unicode=True):
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    # Not JSON - append raw text
                    chunks.append(line)
                    continue

                # Common incremental fields returned by Ollama
                if isinstance(obj, dict):
                    if "response" in obj:
                        chunks.append(
                            obj["response"]
                            if isinstance(obj["response"], str)
                            else json.dumps(obj["response"])
                        )
                    elif "output" in obj:
                        chunks.append(
                            obj["output"]
                            if isinstance(obj["output"], str)
                            else json.dumps(obj["output"])
                        )
                    elif "text" in obj:
                        chunks.append(
                            obj["text"]
                            if isinstance(obj["text"], str)
                            else json.dumps(obj["text"])
                        )

                    # If the stream signals completion, stop consuming
                    if obj.get("done") is True:
                        break

        if chunks:
            return "".join(chunks)

        # Fallback: if nothing was streamed, try a normal JSON parse of the
        # last response body (requests will have consumed it above in
        # non-streaming cases, but keep this defensive path).
        try:
            # Re-run a simple non-streaming request (longer timeout for model loading)
            resp = requests.post(url, json=payload, timeout=120)
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            # Last-resort: return an empty string or raw text body
            try:
                return resp.text
            except Exception:
                return ""

        if isinstance(data, dict):
            for k in ("output", "response", "text", "result"):
                if k in data:
                    return data[k] if isinstance(data[k], str) else json.dumps(data[k])
            if (
                "choices" in data
                and isinstance(data["choices"], list)
                and data["choices"]
            ):
                choice = data["choices"][0]
                if "text" in choice:
                    return choice["text"]
            return json.dumps(data)
        return str(data)

    async def _acall(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        logger.info(f"🤖 Calling Ollama LLM (async) with model: {self.model_name}")
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "temperature": self.temperature,
        }
        if self.max_tokens:
            payload["max_tokens"] = self.max_tokens
        if stop:
            payload["stop"] = stop

        url = f"{self.base_url.rstrip('/')}/api/generate"
        chunks: List[str] = []
        # Increased timeout to 300s (5min) to allow model loading on first request
        logger.debug(
            "⏳ Waiting for Ollama response (may take up to 5min on first load)..."
        )
        async with httpx.AsyncClient(timeout=300) as client:
            # Use streaming to consume incremental NDJSON events
            async with client.stream("POST", url, json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except Exception:
                        chunks.append(line)
                        continue

                    if isinstance(obj, dict):
                        if "response" in obj:
                            chunks.append(
                                obj["response"]
                                if isinstance(obj["response"], str)
                                else json.dumps(obj["response"])
                            )
                        elif "output" in obj:
                            chunks.append(
                                obj["output"]
                                if isinstance(obj["output"], str)
                                else json.dumps(obj["output"])
                            )
                        elif "text" in obj:
                            chunks.append(
                                obj["text"]
                                if isinstance(obj["text"], str)
                                else json.dumps(obj["text"])
                            )

                        if obj.get("done") is True:
                            break

        if chunks:
            return "".join(chunks)

        # Fallback: try a simple non-streaming request
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
        except Exception:
            try:
                return resp.text
            except Exception:
                return ""

        if isinstance(data, dict):
            for k in ("output", "response", "text", "result"):
                if k in data:
                    return data[k] if isinstance(data[k], str) else json.dumps(data[k])
            if (
                "choices" in data
                and isinstance(data["choices"], list)
                and data["choices"]
            ):
                choice = data["choices"][0]
                if "text" in choice:
                    return choice["text"]
            return json.dumps(data)
        return str(data)


# Optional thin wrapper similar to your previous LLMClient interface
class LLMClient:
    def __init__(self):
        self.llm = OllamaLLM()

    def generate(self, prompt: str) -> str:
        return self.llm(prompt)

    async def generate_async(self, prompt: str) -> str:
        # Use ainvoke instead of deprecated apredict
        return await self.llm.ainvoke(prompt)
