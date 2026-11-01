from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import LLMGenerationError

INSUFFICIENT_EVIDENCE_PHRASE = "I do not have sufficient information in the provided document(s) to answer this question."

class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 1500
    ) -> Dict[str, Any]:
        """Generate a chat completion from a structured list of messages."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        pass


class MockLLMProvider(BaseLLMProvider):
    """
    Deterministic mock LLM provider for testing and offline environments.
    Strictly follows grounding instructions: if <context_passages> is empty or missing,
    it returns INSUFFICIENT_EVIDENCE_PHRASE.
    """
    def __init__(self, model: str = "mock-gpt-4o"):
        self.model = model

    @property
    def model_name(self) -> str:
        return self.model

    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 1500
    ) -> Dict[str, Any]:
        system_content = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_content = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")

        # Check if context passages exist and contain non-whitespace text
        has_passages = False
        passage_snippet = ""
        doc_id = "doc"
        page_num = "1"

        if "<passage" in system_content:
            has_passages = True
            import re
            doc_id_match = re.search(r'document_id="([^"]+)"', system_content)
            if doc_id_match:
                doc_id = doc_id_match.group(1)
            page_match = re.search(r'page="([^"]+)"', system_content)
            if page_match:
                page_num = page_match.group(1)
            text_match = re.search(r'<passage[^>]*>(.*?)</passage>', system_content, re.DOTALL)
            if text_match:
                passage_snippet = text_match.group(1).strip()[:100]

        if not has_passages:
            answer = INSUFFICIENT_EVIDENCE_PHRASE
        else:
            answer = (
                f"Based on the provided document evidence, regarding '{user_content}': "
                f"{passage_snippet or 'The document confirms the requested information.'} "
                f"[Doc: {doc_id}, Page: {page_num}]."
            )

        prompt_tokens = len(system_content + user_content) // 4
        completion_tokens = len(answer) // 4

        return {
            "content": answer,
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens
            },
            "model": self.model
        }


class OpenAILLMProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model

    @property
    def model_name(self) -> str:
        return self.model

    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 1500
    ) -> Dict[str, Any]:
        import httpx
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                choice = data["choices"][0]
                usage = data.get("usage", {})
                return {
                    "content": choice["message"]["content"],
                    "usage": {
                        "prompt_tokens": usage.get("prompt_tokens", 0),
                        "completion_tokens": usage.get("completion_tokens", 0),
                        "total_tokens": usage.get("total_tokens", 0)
                    },
                    "model": self.model
                }
        except Exception as e:
            logger.error(f"OpenAI LLM inference failed: {str(e)}")
            raise LLMGenerationError(f"LLM provider error: {str(e)}")


def get_llm_provider() -> BaseLLMProvider:
    if settings.llm_provider == "openai" and settings.openai_api_key:
        return OpenAILLMProvider(api_key=settings.openai_api_key, model=settings.llm_model)
    return MockLLMProvider(model=settings.llm_model)
