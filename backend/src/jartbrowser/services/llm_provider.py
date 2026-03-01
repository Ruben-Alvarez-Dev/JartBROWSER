"""LLM Provider Service - Multi-provider support"""

import os
import asyncio
from typing import Optional, Dict, Any, List, AsyncIterator
from abc import ABC, abstractmethod
from dataclasses import dataclass

# Provider imports - with fallbacks
try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

try:
    from anthropic import AsyncAnthropic
except ImportError:
    AsyncAnthropic = None


@dataclass
class LLMResponse:
    """LLM response container"""

    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str


class BaseLLMProvider(ABC):
    """Base class for LLM providers"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name"""
        pass

    @abstractmethod
    async def complete(
        self, prompt: str, model: str, temperature: float = 0.7, max_tokens: int = 4096, **kwargs
    ) -> LLMResponse:
        """Send completion request"""
        pass

    @abstractmethod
    async def stream(
        self, prompt: str, model: str, temperature: float = 0.7, max_tokens: int = 4096, **kwargs
    ) -> AsyncIterator[str]:
        """Stream completion"""
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider"""

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        if AsyncOpenAI is None:
            raise ImportError("openai package not installed")
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    @property
    def name(self) -> str:
        return "openai"

    async def complete(
        self, prompt: str, model: str, temperature: float = 0.7, max_tokens: int = 4096, **kwargs
    ) -> LLMResponse:
        response = await self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
        return LLMResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            finish_reason=response.choices[0].finish_reason,
        )

    async def stream(
        self, prompt: str, model: str, temperature: float = 0.7, max_tokens: int = 4096, **kwargs
    ) -> AsyncIterator[str]:
        response = await self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs,
        )
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class AnthropicProvider(BaseLLMProvider):
    """Anthropic (Claude) provider"""

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        if AsyncAnthropic is None:
            raise ImportError("anthropic package not installed")
        self.client = AsyncAnthropic(api_key=api_key, base_url=base_url)

    @property
    def name(self) -> str:
        return "anthropic"

    async def complete(
        self, prompt: str, model: str, temperature: float = 0.7, max_tokens: int = 4096, **kwargs
    ) -> LLMResponse:
        response = await self.client.messages.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
        return LLMResponse(
            content=response.content[0].text,
            model=response.model,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
            finish_reason=response.stop_reason,
        )

    async def stream(
        self, prompt: str, model: str, temperature: float = 0.7, max_tokens: int = 4096, **kwargs
    ) -> AsyncIterator[str]:
        async with self.client.messages.stream(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        ) as stream:
            async for text in stream.text_stream:
                yield text


class OllamaProvider(BaseLLMProvider):
    """Ollama local provider"""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url

    @property
    def name(self) -> str:
        return "ollama"

    async def complete(
        self, prompt: str, model: str, temperature: float = 0.7, max_tokens: int = 4096, **kwargs
    ) -> LLMResponse:
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    **kwargs,
                },
            ) as response:
                data = await response.json()
                return LLMResponse(
                    content=data.get("response", ""),
                    model=model,
                    usage={"total_tokens": len(prompt) + len(data.get("response", ""))},
                    finish_reason=data.get("done", True) and "stop" or "length",
                )

    async def stream(
        self, prompt: str, model: str, temperature: float = 0.7, max_tokens: int = 4096, **kwargs
    ) -> AsyncIterator[str]:
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": True,
                    **kwargs,
                },
            ) as response:
                async for line in response.content:
                    if line:
                        data = line.decode().strip()
                        if data:
                            try:
                                chunk = eval(data)  # Parse JSON lines
                                if chunk.get("response"):
                                    yield chunk["response"]
                                if chunk.get("done"):
                                    break
                            except:
                                pass


# Provider registry
PROVIDERS: Dict[str, type] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "ollama": OllamaProvider,
    # Add custom providers below
    # "z.ai": ...,  # Z.ai provider
    # "minimax": ...,  # MiniMax provider
    # "mistral": ...,  # Mistral provider
}


def get_provider(
    provider_name: str, api_key: str, base_url: Optional[str] = None
) -> BaseLLMProvider:
    """Get provider instance"""
    provider_class = PROVIDERS.get(provider_name.lower())
    if not provider_class:
        raise ValueError(f"Unknown provider: {provider_name}")
    return provider_class(api_key=api_key, base_url=base_url)


# Model mappings
PROVIDER_MODELS = {
    "openai": ["gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
    "anthropic": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
    "ollama": ["llama2", "mistral", "codellama", "mixtral"],
}
