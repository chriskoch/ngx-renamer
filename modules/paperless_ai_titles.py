import requests
import yaml

from modules.openai_titles import OpenAITitles
from modules.ollama_titles import OllamaTitles


class PaperlessAITitles:
    def __init__(self, openai_api_key, ollama_base_url, paperless_url, paperless_api_key, settings_file="settings.yaml"):
        """Initialize Paperless AI Titles orchestrator.

        Args:
            openai_api_key: OpenAI API key (required if using OpenAI provider)
            ollama_base_url: Ollama base URL (required if using Ollama provider)
            paperless_url: Paperless NGX API URL
            paperless_api_key: Paperless NGX API key
            settings_file: Path to settings.yaml configuration file
        """
        self.openai_api_key = openai_api_key
        self.ollama_base_url = ollama_base_url
        self.paperless_url = paperless_url
        self.paperless_api_key = paperless_api_key
        self.settings_file = settings_file

        # Load settings to determine provider
        self.settings = self._load_settings(settings_file)

        # Create appropriate LLM provider based on settings
        self.ai = self._create_llm_provider()

    def _load_settings(self, settings_file):
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
            print(f"Error loading settings file: {e}")
            return {}

    def _create_llm_provider(self):
        """Factory method to create the appropriate LLM provider based on settings.

        Returns:
            BaseLLMProvider: Instance of OpenAITitles or OllamaTitles

        Raises:
            ValueError: If provider is unknown or required credentials are missing
        """
        # Get provider from settings, default to "openai" for backward compatibility
        provider = self.settings.get("llm_provider", "openai").lower()

        if provider == "openai":
            if not self.openai_api_key:
                raise ValueError(
                    "OPENAI_API_KEY environment variable is required when using OpenAI provider.\n"
                    "Either set OPENAI_API_KEY or change llm_provider to 'ollama' in settings.yaml"
                )
            return OpenAITitles(self.openai_api_key, self.settings_file)

        elif provider == "ollama":
            if not self.ollama_base_url:
                raise ValueError(
                    "OLLAMA_BASE_URL environment variable is required when using Ollama provider.\n"
                    "Either set OLLAMA_BASE_URL or change llm_provider to 'openai' in settings.yaml"
                )
            return OllamaTitles(self.ollama_base_url, self.settings_file)

        else:
            raise ValueError(
                f"Unknown LLM provider '{provider}'. Valid options: 'openai', 'ollama'\n"
                f"Check the 'llm_provider' setting in {self.settings_file}"
            )


    def __get_document_details(self, document_id):
        headers = {
            "Authorization": f"Token {self.paperless_api_key}",
            "Content-Type": "application/json",
        }

        response = requests.get(
            f"{self.paperless_url}/documents/{document_id}/", headers=headers
        )

        if response.status_code == 200:
            return response.json()
        else:
            print(
                f"Failed to get document details from paperless-ngx. Status code: {response.status_code}"
            )
            print(response.text)
            return None


    def __update_document_title(self, document_id, new_title):
        payload = {"title": new_title}

        headers = {
            "Authorization": f"Token {self.paperless_api_key}",
            "Content-Type": "application/json",
        }

        response = requests.patch(
            f"{self.paperless_url}/documents/{document_id}/",
            json=payload,
            headers=headers,
        )

        if response.status_code == 200:
            print(
                f"Title of {document_id} successfully updated in paperless-ngx to {new_title}."
            )
        else:
            print(
                f"Failed to update title in paperless-ngx. Status code: {response.status_code}"
            )
            print(response.text)


    def generate_and_update_title(self, document_id):
        document_details = self.__get_document_details(document_id)
        if document_details:
            print(f"Current Document Title: {document_details['title']}")

            content = document_details.get("content", "")

            new_title = self.ai.generate_title_from_text(content)

            if new_title:
                print(f"Generated Document Title: {new_title}")

                self.__update_document_title(document_id, new_title)
            else:
                print("Failed to generate the document title.")
        else:
            print("Failed to retrieve document details.")
