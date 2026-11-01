from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.core.config import settings
from app.core.logging import logger

class ILLMClient(ABC):
    @abstractmethod
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0
    ) -> Dict[str, Any]:
        pass


class MockLLMClient(ILLMClient):
    """
    Deterministic mock LLM generator for local development and testing.
    Synthesizes a response directly citing retrieved passages.
    """
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0
    ) -> Dict[str, Any]:
        user_message = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        
        # Check if context passages are present
        system_message = next((m["content"] for m in messages if m["role"] == "system"), "")
        
        if "<context_passages>" in system_message:
            answer = (
                f"Based on the provided document passages, here is the answer regarding '{user_message}': "
                f"The referenced documents substantiate this analysis. [Citation: Page 1]"
            )
        else:
            answer = "I do not have sufficient information in the provided document(s) to answer this question."

        return {
            "content": answer,
            "prompt_tokens": len(system_message + user_message) // 4,
            "completion_tokens": len(answer) // 4,
            "model": "mock-llm-v1"
        }


class OpenAILLMClient(ILLMClient):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model

    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0
    ) -> Dict[str, Any]:
        import httpx
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature
        }

        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            choice = data["choices"][0]
            usage = data.get("usage", {})
            return {
                "content": choice["message"]["content"],
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "model": self.model
            }


def get_llm_client() -> ILLMClient:
    if settings.llm_provider == "openai" and settings.openai_api_key:
        return OpenAILLMClient(api_key=settings.openai_api_key, model=settings.llm_model)
    return MockLLMClient()

