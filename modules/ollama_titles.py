"""Ollama LLM provider for title generation."""
from typing import Optional, Dict, Any
import ollama
from modules.base_llm_provider import BaseLLMProvider
from modules.logger import get_logger
from modules.constants import TITLE_SCHEMA, DEFAULT_MODELS, MAX_TITLE_LENGTH, PROVIDER_OLLAMA


class OllamaTitles(BaseLLMProvider):
    """Ollama-based title generation provider.

    Uses the Ollama API to generate document titles from text content.
    Requires Ollama to be running locally or accessible via network.
    """

    def __init__(
        self,
        ollama_base_url: str,
        api_key: Optional[str] = None,
        settings_file: str = "settings.yaml"
    ) -> None:
        """Initialize Ollama provider.

        Args:
            ollama_base_url: URL of Ollama API (e.g., http://localhost:11434)
            api_key: Optional API key for authenticated Ollama instances (default: None)
            settings_file: Path to settings.yaml configuration file
        """
        super().__init__(settings_file)
        self.ollama_base_url = ollama_base_url
        self.api_key = api_key
        
        headers = {}

        # Add authentication header if API key is provided
        if api_key and api_key.strip():
            headers["Authorization"] = f"Bearer {api_key}"
        
        self._client = ollama.Client(host=ollama_base_url, headers=headers)

    def _call_ollama_api(self, content: str, role: str = "user") -> Optional[Dict[str, Any]]:
        """Call Ollama chat completion API.

        Args:
            content: The prompt/content to send to Ollama
            role: Message role (default: "user")

        Returns:
            Ollama response dict, or None on error
        """
        try:
            # Get model from settings
            if "ollama" in self.settings and isinstance(self.settings["ollama"], dict):
                model = self.settings["ollama"].get("model", DEFAULT_MODELS[PROVIDER_OLLAMA])
            else:
                model = DEFAULT_MODELS[PROVIDER_OLLAMA]

            # Pass JSON schema directly to format parameter
            # Ollama Python client accepts: Union[Literal['', 'json'], dict[str, Any], None]
            # We pass the schema dict directly (recommended for structured outputs)
            response = self._client.chat(
                model=model,
                messages=[
                    {
                        "role": role,
                        "content": content,
                    },
                ],
                format=TITLE_SCHEMA,
            )
            return response
        except ollama.ResponseError as e:
            error_msg = str(e).lower()
            if "not found" in error_msg or "model" in error_msg:
                model = self.settings.get("ollama", {}).get("model", DEFAULT_MODELS[PROVIDER_OLLAMA])
                self._logger.error(f"Model '{model}' not found in Ollama")
                self._logger.error(f"Please pull the model first: ollama pull {model}")
            else:
                self._logger.error(f"Error generating title from Ollama (API error): {e}")
            return None
        except Exception as e:
            self._logger.error(f"Error generating title from Ollama: {e}")
            self._logger.error(f"Make sure Ollama is running at {self.ollama_base_url}")
            self._logger.error(f"You can test with: curl {self.ollama_base_url}/api/version")
            return None

    def generate_title_from_text(self, text: str) -> Optional[str]:
        """Generate a title from text using Ollama.

        Args:
            text: Document content to generate title from

        Returns:
            str: Generated title, or None if generation failed
        """
        prompt = self._build_prompt(text)
        if not prompt:
            return None

        result = self._call_ollama_api(prompt)
        if result:
            try:
                content = result['message']['content']
                return self._parse_structured_response(content)
            except (KeyError, TypeError) as e:
                self._logger.error(f"Unexpected response structure from Ollama: {e}")
                self._logger.error(f"Response: {result}")
                return None

        return None
