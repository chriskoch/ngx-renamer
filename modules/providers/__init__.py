"""Provider registry and auto-discovery for LLM providers."""

from typing import Dict, Type
from modules.base_llm_provider import BaseLLMProvider

# Provider registry - maps provider names to classes
_PROVIDER_REGISTRY: Dict[str, Type[BaseLLMProvider]] = {}


def register_provider(name: str, provider_class: Type[BaseLLMProvider]) -> None:
    """Register a new LLM provider.

    Args:
        name: Provider name (e.g., "openai", "ollama", "claude")
        provider_class: Provider class that inherits from BaseLLMProvider
    """
    _PROVIDER_REGISTRY[name.lower()] = provider_class


def get_provider_class(name: str) -> Type[BaseLLMProvider]:
    """Get provider class by name.

    Args:
        name: Provider name

    Returns:
        Provider class

    Raises:
        ValueError: If provider not found
    """
    provider_class = _PROVIDER_REGISTRY.get(name.lower())
    if not provider_class:
        available = ", ".join(sorted(_PROVIDER_REGISTRY.keys()))
        raise ValueError(
            f"Unknown LLM provider '{name}'. "
            f"Available providers: {available}"
        )
    return provider_class


def list_providers() -> list[str]:
    """List all registered provider names.

    Returns:
        List of provider names
    """
    return sorted(_PROVIDER_REGISTRY.keys())


# Auto-register providers from this directory
# For now, we'll import and register manually to maintain backward compatibility
# In the future, this could scan the directory automatically

from modules.ollama_titles import OllamaTitles  # noqa: E402
from modules.openai_titles import OpenAITitles  # noqa: E402

register_provider("ollama", OllamaTitles)
register_provider("openai", OpenAITitles)
