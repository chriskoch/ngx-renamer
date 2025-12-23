"""Factory for creating LLM provider instances."""

from typing import Optional
from modules.base_llm_provider import BaseLLMProvider
from modules.logger import get_logger
from modules.constants import PROVIDER_OPENAI, PROVIDER_OLLAMA
from modules.providers import get_provider_class


class LLMFactory:
    """Factory for creating LLM provider instances based on configuration."""

    def __init__(self) -> None:
        self._logger = get_logger(self.__class__.__name__)

    def create_provider(
        self,
        provider_name: str,
        openai_api_key: Optional[str],
        ollama_base_url: Optional[str],
        ollama_api_key: Optional[str],
        settings_file: str
    ) -> BaseLLMProvider:
        """Create appropriate LLM provider based on configuration.

        Args:
            provider_name: Name of provider ("openai" or "ollama")
            openai_api_key: OpenAI API key (required for OpenAI)
            ollama_base_url: Ollama base URL (required for Ollama)
            ollama_api_key: Ollama API key (optional)
            settings_file: Path to settings.yaml

        Returns:
            BaseLLMProvider: Instance of requested provider

        Raises:
            ValueError: If provider is unknown or credentials missing
        """
        provider = provider_name.lower()

        # Get provider class from registry
        provider_class = get_provider_class(provider)

        # Create provider with appropriate credentials
        if provider == PROVIDER_OPENAI:
            return self._create_openai_provider(
                provider_class, openai_api_key, settings_file
            )
        elif provider == PROVIDER_OLLAMA:
            return self._create_ollama_provider(
                provider_class, ollama_base_url, ollama_api_key, settings_file
            )
        else:
            # This shouldn't happen if registry is working correctly,
            # but handle it gracefully
            raise ValueError(f"Unhandled provider: {provider}")

    def _create_openai_provider(
        self,
        provider_class,
        api_key: Optional[str],
        settings_file: str
    ) -> BaseLLMProvider:
        """Create OpenAI provider instance."""
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required when using "
                "OpenAI provider. Either set OPENAI_API_KEY or change "
                "llm_provider to 'ollama' in settings.yaml"
            )

        self._logger.info(f"Creating OpenAI provider with settings: {settings_file}")
        return provider_class(api_key, settings_file)

    def _create_ollama_provider(
        self,
        provider_class,
        base_url: Optional[str],
        api_key: Optional[str],
        settings_file: str
    ) -> BaseLLMProvider:
        """Create Ollama provider instance."""
        if not base_url:
            raise ValueError(
                "OLLAMA_BASE_URL environment variable is required when using "
                "Ollama provider. Either set OLLAMA_BASE_URL or change "
                "llm_provider to 'openai' in settings.yaml"
            )

        self._logger.info(f"Creating Ollama provider at {base_url}")
        return provider_class(base_url, api_key, settings_file)
