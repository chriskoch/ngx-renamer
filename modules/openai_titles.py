from typing import Optional
from openai import OpenAI
from openai.types.chat import ChatCompletion
from modules.base_llm_provider import BaseLLMProvider
from modules.logger import get_logger
from modules.constants import TITLE_SCHEMA, DEFAULT_MODELS, MAX_TITLE_LENGTH, PROVIDER_OPENAI


class OpenAITitles(BaseLLMProvider):
    """OpenAI-based title generation provider.

    Uses the OpenAI API to generate document titles from text content.
    """

    def __init__(self, openai_api_key: str, settings_file: str = "settings.yaml") -> None:
        """Initialize OpenAI provider.

        Args:
            openai_api_key: OpenAI API key for authentication
            settings_file: Path to settings.yaml configuration file
        """
        super().__init__(settings_file)
        self._openai_client = OpenAI(api_key=openai_api_key)

    def _call_openai_api(self, content: str, role: str = "user") -> Optional[ChatCompletion]:
        """Call OpenAI chat completion API.

        Args:
            content: The prompt/content to send to OpenAI
            role: Message role (default: "user")

        Returns:
            OpenAI response object, or None on error
        """
        try:
            # Support both new and legacy settings structure
            # New structure: settings["openai"]["model"]
            # Legacy structure: settings["openai_model"]
            if "openai" in self.settings and isinstance(self.settings["openai"], dict):
                model = self.settings["openai"].get("model", DEFAULT_MODELS[PROVIDER_OPENAI])
            else:
                # Backward compatibility - check root level
                model = self.settings.get("openai_model", DEFAULT_MODELS[PROVIDER_OPENAI])

            res = self._openai_client.chat.completions.create(
                messages=[
                    {
                        "role": role,
                        "content": content,
                    },
                ],
                model=model,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "document_title",
                        "schema": TITLE_SCHEMA,
                        "strict": True
                    }
                }
            )
            return res
        except Exception as e:
            self._logger.error(f"Error generating title from GPT: {e}")
            return None

    def generate_title_from_text(self, text: str) -> Optional[str]:
        """Generate a title from text using OpenAI.

        Args:
            text: Document content to generate title from

        Returns:
            str: Generated title, or None if generation failed
        """
        prompt = self._build_prompt(text)
        if not prompt:
            return None

        result = self._call_openai_api(prompt)
        if result:
            content = result.choices[0].message.content
            return self._parse_structured_response(content)

        return None
