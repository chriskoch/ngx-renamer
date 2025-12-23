from typing import Optional, Dict, Any
import yaml

from modules.base_llm_provider import BaseLLMProvider
from modules.llm_factory import LLMFactory
from modules.paperless_client import PaperlessClient
from modules.exceptions import PaperlessAPIError
from modules.logger import get_logger
from modules.constants import PROVIDER_OPENAI


class PaperlessAITitles:
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        ollama_base_url: Optional[str] = None,
        ollama_api_key: Optional[str] = None,
        paperless_url: str = None,
        paperless_api_key: str = None,
        settings_file: str = "settings.yaml"
    ) -> None:
        """Initialize Paperless AI Titles orchestrator.

        Args:
            openai_api_key: OpenAI API key (required if using OpenAI provider)
            ollama_base_url: Ollama base URL (required if using Ollama provider)
            ollama_api_key: Ollama API key (optional, for authenticated Ollama instances)
            paperless_url: Paperless NGX API URL
            paperless_api_key: Paperless NGX API key
            settings_file: Path to settings.yaml configuration file
        """
        self._logger = get_logger(self.__class__.__name__)
        self._settings_file = settings_file
        self.settings = self._load_settings(settings_file)

        # Create Paperless API client
        self._paperless = PaperlessClient(paperless_url, paperless_api_key)

        # Create LLM provider using factory
        factory = LLMFactory()
        provider_name = self.settings.get("llm_provider", PROVIDER_OPENAI)

        self._llm_provider = factory.create_provider(
            provider_name=provider_name,
            openai_api_key=openai_api_key,
            ollama_base_url=ollama_base_url,
            ollama_api_key=ollama_api_key,
            settings_file=settings_file
        )

        self._logger.info(
            f"Initialized with provider: {provider_name}, "
            f"settings: {settings_file}"
        )

    def _load_settings(self, settings_file: str) -> Dict[str, Any]:
        """Load settings from YAML file.

        Args:
            settings_file: Path to YAML settings file

        Returns:
            dict: Loaded settings, or empty dict if loading fails
        """
        try:
            with open(settings_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self._logger.error(f"Error loading settings file: {e}", exc_info=True)
            return {}

    # Backward compatibility property
    @property
    def ai(self) -> BaseLLMProvider:
        """Backward compatibility: access to LLM provider."""
        return self._llm_provider


    def generate_and_update_title(self, document_id: str) -> None:
        """Generate AI title and update document in Paperless NGX.

        Args:
            document_id: Paperless document ID to process
        """
        try:
            # Fetch document details
            document = self._paperless.get_document(document_id)
            current_title = document.get('title', 'Unknown')

            self._logger.info(f"Current Document Title: {current_title}")

            # Extract content
            content = document.get("content", "")
            if not content:
                self._logger.warning(
                    f"Document {document_id} has no content, skipping"
                )
                return

            # Generate new title
            new_title = self._llm_provider.generate_title_from_text(content)

            if new_title:
                self._logger.info(f"Generated Document Title: {new_title}")
                self._paperless.update_document_title(document_id, new_title)
            else:
                self._logger.error("Failed to generate document title")

        except PaperlessAPIError as e:
            self._logger.error(f"Paperless API error: {e}")
        except Exception as e:
            self._logger.error(
                f"Unexpected error processing document {document_id}: {e}",
                exc_info=True
            )
