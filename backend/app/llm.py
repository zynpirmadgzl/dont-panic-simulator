"""
Custom LLM Engine targeting qwen-397b via direct HTTP API.
Bypasses OpenAI SDK header restrictions and handles Qwen reasoning tags.
"""
import os
import re
import json
import asyncio
import httpx
from typing import List
from dotenv import load_dotenv

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration

load_dotenv()


class CustomQwenLLM(BaseChatModel):
    model_name: str = "qwen-397b"
    api_key: str = ""
    base_url: str = ""
    temperature: float = 0.7

    @property
    def _llm_type(self) -> str:
        return "custom-qwen-397b"

    def _generate(self, messages: List[BaseMessage], stop=None, run_manager=None, **kwargs) -> ChatResult:
        # Fallback sync wrapper
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(self._agenerate(messages, stop=stop, run_manager=run_manager, **kwargs))

    async def _agenerate(self, messages: List[BaseMessage], stop=None, run_manager=None, **kwargs) -> ChatResult:
        formatted_messages = []
        for m in messages:
            role = "user"
            if m.type == "system":
                role = "system"
            elif m.type == "ai":
                role = "assistant"
            formatted_messages.append({"role": role, "content": str(m.content)})

        url = f"{self.base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        }
        payload = {
            "model": self.model_name,
            "messages": formatted_messages,
            "temperature": self.temperature,
            "response_format": {"type": "json_object"}
        }

        async with httpx.AsyncClient(verify=False, timeout=httpx.Timeout(300.0, connect=30.0)) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

            raw_content = data["choices"][0]["message"]["content"]

            # Remove <think>...</think> reasoning blocks if output by Qwen
            cleaned_content = raw_content
            if "</think>" in cleaned_content:
                cleaned_content = cleaned_content.split("</think>")[-1].strip()

            # Sanitize invalid leading plus signs in JSON numbers (e.g. "+8" -> "8", "+2.5" -> "2.5")
            cleaned_content = re.sub(r':\s*\+(\d+(\.\d+)?)', r': \1', cleaned_content)

            message = AIMessage(content=cleaned_content)
            generation = ChatGeneration(message=message)
            return ChatResult(generations=[generation])


def get_llm(temperature: float = 0.7) -> BaseChatModel:
    """
    Constructs and returns CustomQwenLLM targeting qwen-397b on llmstat.iletisim.gov.tr.
    """
    raw_api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or ""
    raw_base_url = os.getenv("LLM_BASE_URL") or "https://api.openai.com/v1"
    raw_model_name = os.getenv("LLM_MODEL") or "qwen-397b"

    api_key = raw_api_key.strip(" \"'\t\n\r")
    base_url = raw_base_url.strip(" \"'\t\n\r").rstrip("/")
    model_name = raw_model_name.strip(" \"'\t\n\r")

    if not api_key or api_key == "your_actual_api_key_here":
        raise ValueError(
            "LLM_API_KEY is not set or contains default placeholder. "
            "Please update backend/.env with your valid API key."
        )

    return CustomQwenLLM(
        model_name=model_name,
        api_key=api_key,
        base_url=base_url,
        temperature=temperature
    )
