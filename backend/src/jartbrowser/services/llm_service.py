"""
LLM Service - Complete LLM Integration

Provides unified interface for multiple LLM providers,
model selection, and token tracking.
"""

import os
import json
import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, AsyncIterator, Union

# Provider imports
try:
    import openai
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

try:
    import anthropic
    from anthropic import AsyncAnthropic
except ImportError:
    AsyncAnthropic = None


# ============== Data Classes ==============


@dataclass
class ModelInfo:
    """Information about an LLM model"""

    id: str
    name: str
    provider: str
    context_window: int
    max_output_tokens: int
    supports_vision: bool = False
    supports_streaming: bool = True
    input_cost_per_1k: float = 0.0
    output_cost_per_1k: float = 0.0


@dataclass
class LLMResponse:
    """LLM API response"""

    content: str
    model: str
    provider: str
    usage: Dict[str, int]
    finish_reason: str
    response_id: str
    latency_ms: int


@dataclass
class ConversationMessage:
    """Conversation message"""

    role: str  # system, user, assistant
    content: str
    images: Optional[List[str]] = None  # base64 encoded images for vision


@dataclass
class Conversation:
    """LLM conversation"""

    id: str
    messages: List[ConversationMessage] = field(default_factory=list)
    model: str = "gpt-4o"
    provider: str = "openai"
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============== Model Registry ==============

MODEL_REGISTRY: Dict[str, ModelInfo] = {
    # OpenAI Models
    "gpt-4o": ModelInfo(
        id="gpt-4o",
        name="GPT-4o",
        provider="openai",
        context_window=128000,
        max_output_tokens=16384,
        supports_vision=True,
        input_cost_per_1k=5.0,
        output_cost_per_1k=15.0,
    ),
    "gpt-4-turbo": ModelInfo(
        id="gpt-4-turbo",
        name="GPT-4 Turbo",
        provider="openai",
        context_window=128000,
        max_output_tokens=4096,
        supports_vision=True,
        input_cost_per_1k=10.0,
        output_cost_per_1k=30.0,
    ),
    "gpt-4": ModelInfo(
        id="gpt-4",
        name="GPT-4",
        provider="openai",
        context_window=8192,
        max_output_tokens=4096,
        input_cost_per_1k=30.0,
        output_cost_per_1k=60.0,
    ),
    "gpt-3.5-turbo": ModelInfo(
        id="gpt-3.5-turbo",
        name="GPT-3.5 Turbo",
        provider="openai",
        context_window=16385,
        max_output_tokens=4096,
        input_cost_per_1k=0.5,
        output_cost_per_1k=1.5,
    ),
    # Anthropic Models
    "claude-3-5-sonnet": ModelInfo(
        id="claude-3-5-sonnet",
        name="Claude 3.5 Sonnet",
        provider="anthropic",
        context_window=200000,
        max_output_tokens=8192,
        supports_vision=True,
        input_cost_per_1k=3.0,
        output_cost_per_1k=15.0,
    ),
    "claude-3-opus": ModelInfo(
        id="claude-3-opus",
        name="Claude 3 Opus",
        provider="anthropic",
        context_window=200000,
        max_output_tokens=4096,
        supports_vision=True,
        input_cost_per_1k=15.0,
        output_cost_per_1k=75.0,
    ),
    "claude-3-haiku": ModelInfo(
        id="claude-3-haiku",
        name="Claude 3 Haiku",
        provider="anthropic",
        context_window=200000,
        max_output_tokens=4096,
        supports_vision=True,
        input_cost_per_1k=0.25,
        output_cost_per_1k=1.25,
    ),
    # Ollama Models (local)
    "llama2": ModelInfo(
        id="llama2",
        name="Llama 2",
        provider="ollama",
        context_window=4096,
        max_output_tokens=2048,
        input_cost_per_1k=0.0,
        output_cost_per_1k=0.0,
    ),
    "mistral": ModelInfo(
        id="mistral",
        name="Mistral",
        provider="ollama",
        context_window=8192,
        max_output_tokens=4096,
        input_cost_per_1k=0.0,
        output_cost_per_1k=0.0,
    ),
    "codellama": ModelInfo(
        id="codellama",
        name="Code Llama",
        provider="ollama",
        context_window=16384,
        max_output_tokens=4096,
        input_cost_per_1k=0.0,
        output_cost_per_1k=0.0,
    ),
}


# ============== Provider Classes ==============


class BaseLLMProvider:
    """Base class for LLM providers"""

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url

    @property
    def name(self) -> str:
        raise NotImplementedError

    async def complete(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> LLMResponse:
        raise NotImplementedError

    async def stream(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> AsyncIterator[str]:
        raise NotImplementedError

    async def embed(self, text: str, model: str = "text-embedding-3-small") -> List[float]:
        raise NotImplementedError


class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider implementation"""

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        super().__init__(api_key, base_url)
        if AsyncOpenAI:
            self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        else:
            raise ImportError("openai package not installed")

    @property
    def name(self) -> str:
        return "openai"

    async def complete(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> LLMResponse:
        start_time = asyncio.get_event_loop().time()

        response = await self.client.chat.completions.create(
            model=model, messages=messages, temperature=temperature, max_tokens=max_tokens, **kwargs
        )

        latency_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)

        return LLMResponse(
            content=response.choices[0].message.content or "",
            model=response.model,
            provider="openai",
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            finish_reason=response.choices[0].finish_reason,
            response_id=response.id,
            latency_ms=latency_ms,
        )

    async def stream(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> AsyncIterator[str]:
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs,
        )

        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def embed(self, text: str, model: str = "text-embedding-3-small") -> List[float]:
        response = await self.client.embeddings.create(model=model, input=text)
        return response.data[0].embedding


class AnthropicProvider(BaseLLMProvider):
    """Anthropic (Claude) provider implementation"""

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        super().__init__(api_key, base_url)
        if AsyncAnthropic:
            self.client = AsyncAnthropic(api_key=api_key, base_url=base_url)
        else:
            raise ImportError("anthropic package not installed")

    @property
    def name(self) -> str:
        return "anthropic"

    def _convert_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert OpenAI-style messages to Anthropic format"""
        converted = []
        for msg in messages:
            if msg["role"] == "system":
                # Prepend to first user message or create system message
                converted.append({"role": "user", "content": f"System: {msg['content']}"})
            else:
                converted.append(msg)
        return converted

    async def complete(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> LLMResponse:
        start_time = asyncio.get_event_loop().time()

        # Map model names
        model_map = {
            "claude-3-5-sonnet": "claude-sonnet-3-5-20241022",
            "claude-3-opus": "claude-3-opus-20240229",
            "claude-3-haiku": "claude-3-haiku-20240307",
        }

        anthropic_model = model_map.get(model, model)

        response = await self.client.messages.create(
            model=anthropic_model,
            messages=self._convert_messages(messages),
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

        latency_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)

        return LLMResponse(
            content=response.content[0].text if response.content else "",
            model=model,
            provider="anthropic",
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            },
            finish_reason=response.stop_reason or "complete",
            response_id=response.id,
            latency_ms=latency_ms,
        )

    async def stream(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> AsyncIterator[str]:
        model_map = {
            "claude-3-5-sonnet": "claude-sonnet-3-5-20241022",
            "claude-3-opus": "claude-3-opus-20240229",
            "claude-3-haiku": "claude-3-haiku-20240307",
        }

        anthropic_model = model_map.get(model, model)

        async with self.client.messages.stream(
            model=anthropic_model,
            messages=self._convert_messages(messages),
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        ) as stream:
            async for text in stream.text_stream:
                yield text

    async def embed(self, text: str, model: str = "claude-embedding-3") -> List[float]:
        # Anthropic doesn't have embeddings API yet
        raise NotImplementedError("Anthropic doesn't support embeddings")


class OllamaProvider(BaseLLMProvider):
    """Ollama local provider"""

    def __init__(self, api_key: str = "", base_url: str = "http://localhost:11434"):
        super().__init__(api_key, base_url)

    @property
    def name(self) -> str:
        return "ollama"

    async def complete(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> LLMResponse:
        import aiohttp

        # Convert messages to prompt
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])

        start_time = asyncio.get_event_loop().time()

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

        latency_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)

        content = data.get("response", "")

        return LLMResponse(
            content=content,
            model=model,
            provider="ollama",
            usage={"total_tokens": len(prompt) + len(content)},
            finish_reason="stop",
            response_id=data.get("id", ""),
            latency_ms=latency_ms,
        )

    async def stream(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> AsyncIterator[str]:
        import aiohttp

        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])

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
                        try:
                            data = json.loads(line.decode().strip())
                            if data.get("response"):
                                yield data["response"]
                            if data.get("done"):
                                break
                        except:
                            pass

    async def embed(self, text: str, model: str = "nomic-embed-text") -> List[float]:
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/embeddings", json={"model": model, "prompt": text}
            ) as response:
                data = await response.json()
                return data.get("embedding", [])


# ============== Provider Registry ==============

PROVIDER_CLASSES: Dict[str, type] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "ollama": OllamaProvider,
}


# ============== Main LLM Service ==============


class LLMService:
    """
    Unified LLM service supporting multiple providers.

    Provides:
    - Multi-provider support (OpenAI, Anthropic, Ollama)
    - Model selection and configuration
    - Conversation management
    - Token tracking and cost estimation
    - Streaming support
    """

    def __init__(self):
        self._providers: Dict[str, BaseLLMProvider] = {}
        self._api_keys: Dict[str, str] = {}
        self._default_provider: str = "openai"
        self._default_model: str = "gpt-4o"
        self._conversations: Dict[str, Conversation] = {}
        self._total_tokens_used: Dict[str, int] = {"openai": 0, "anthropic": 0, "ollama": 0}

    # ============== Configuration ==============

    def set_api_key(self, provider: str, api_key: str) -> None:
        """Set API key for a provider"""
        self._api_keys[provider] = api_key

        # Create provider instance
        if provider in PROVIDER_CLASSES:
            provider_class = PROVIDER_CLASSES[provider]
            try:
                self._providers[provider] = provider_class(api_key)
            except ImportError as e:
                print(f"Warning: Could not initialize {provider}: {e}")

    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a provider"""
        return self._api_keys.get(provider)

    def set_default(self, provider: str, model: str) -> None:
        """Set default provider and model"""
        if provider not in MODEL_REGISTRY:
            raise ValueError(f"Unknown provider: {provider}")

        self._default_provider = provider
        self._default_model = model

    def get_default(self) -> tuple[str, str]:
        """Get default provider and model"""
        return self._default_provider, self._default_model

    # ============== Models ==============

    def get_models(self, provider: Optional[str] = None) -> List[ModelInfo]:
        """Get available models"""
        if provider:
            return [m for m in MODEL_REGISTRY.values() if m.provider == provider]
        return list(MODEL_REGISTRY.values())

    def get_model_info(self, model: str) -> Optional[ModelInfo]:
        """Get information about a specific model"""
        return MODEL_REGISTRY.get(model)

    def get_providers(self) -> List[str]:
        """Get available providers"""
        return list(set(m.provider for m in MODEL_REGISTRY.values()))

    # ============== Completion ==============

    def _get_provider(self, provider: str) -> BaseLLMProvider:
        """Get or create provider instance"""
        if provider in self._providers:
            return self._providers[provider]

        # Create new provider
        if provider in PROVIDER_CLASSES:
            api_key = self._api_keys.get(provider, "")
            self._providers[provider] = PROVIDER_CLASSES[provider](api_key)
            return self._providers[provider]

        raise ValueError(f"Unknown provider: {provider}")

    async def complete(
        self,
        prompt: Union[str, List[Dict[str, Any]]],
        model: Optional[str] = None,
        provider: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> LLMResponse:
        """Send a completion request"""
        # Determine provider and model
        if provider is None:
            provider = self._default_provider
        if model is None:
            model = self._default_model

        # Convert string prompt to messages format
        if isinstance(prompt, str):
            messages = [{"role": "user", "content": prompt}]
        else:
            messages = prompt

        # Get provider
        llm_provider = self._get_provider(provider)

        # Make request
        response = await llm_provider.complete(
            messages=messages, model=model, temperature=temperature, max_tokens=max_tokens, **kwargs
        )

        # Track usage
        if provider in self._total_tokens_used:
            self._total_tokens_used[provider] += response.usage.get("total_tokens", 0)

        return response

    async def stream(
        self,
        prompt: Union[str, List[Dict[str, Any]]],
        model: Optional[str] = None,
        provider: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> AsyncIterator[str]:
        """Stream completion response"""
        if provider is None:
            provider = self._default_provider
        if model is None:
            model = self._default_model

        if isinstance(prompt, str):
            messages = [{"role": "user", "content": prompt}]
        else:
            messages = prompt

        llm_provider = self._get_provider(provider)

        async for chunk in llm_provider.stream(
            messages=messages, model=model, temperature=temperature, max_tokens=max_tokens, **kwargs
        ):
            yield chunk

    # ============== Conversations ==============

    def create_conversation(
        self,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ) -> Conversation:
        """Create a new conversation"""
        import uuid

        conv = Conversation(
            id=str(uuid.uuid4()),
            model=model or self._default_model,
            provider=provider or self._default_provider,
        )

        if system_prompt:
            conv.messages.append(ConversationMessage(role="system", content=system_prompt))

        self._conversations[conv.id] = conv
        return conv

    def get_conversation(self, conv_id: str) -> Optional[Conversation]:
        """Get a conversation"""
        return self._conversations.get(conv_id)

    async def send_message(
        self, conv_id: str, content: str, temperature: float = 0.7, max_tokens: int = 4096
    ) -> LLMResponse:
        """Send a message in a conversation"""
        conv = self._conversations.get(conv_id)
        if not conv:
            raise ValueError(f"Conversation not found: {conv_id}")

        # Add user message
        conv.messages.append(ConversationMessage(role="user", content=content))

        # Convert to API format
        messages = [{"role": m.role, "content": m.content} for m in conv.messages]

        # Get response
        response = await self.complete(
            messages,
            model=conv.model,
            provider=conv.provider,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Add assistant message
        conv.messages.append(ConversationMessage(role="assistant", content=response.content))

        return response

    def delete_conversation(self, conv_id: str) -> bool:
        """Delete a conversation"""
        if conv_id in self._conversations:
            del self._conversations[conv_id]
            return True
        return False

    # ============== Statistics ==============

    def get_usage_stats(self) -> Dict[str, int]:
        """Get total token usage by provider"""
        return self._total_tokens_used.copy()

    def estimate_cost(self, provider: str) -> float:
        """Estimate total cost for a provider"""
        tokens = self._total_tokens_used.get(provider, 0)

        # Get average cost per 1k tokens
        models = self.get_models(provider)
        if not models:
            return 0.0

        avg_input = sum(m.input_cost_per_1k for m in models) / len(models)
        avg_output = sum(m.output_cost_per_1k for m in models) / len(models)

        # Assume 30% input, 70% output
        return (tokens * 0.3 * avg_input + tokens * 0.7 * avg_output) / 1000


# Singleton
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get the LLM service instance"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
