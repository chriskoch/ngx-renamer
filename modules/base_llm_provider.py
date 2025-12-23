"""Base abstract class for LLM providers in ngx-renamer."""
from abc import ABC, abstractmethod
from datetime import datetime
import json
from typing import Optional, Dict, Any
import yaml
from modules.logger import get_logger
from modules.constants import MAX_TITLE_LENGTH


class BaseLLMProvider(ABC):
    """Abstract base class for LLM title generation providers.

    All LLM providers (OpenAI, Ollama, etc.) must inherit from this class
    and implement the generate_title_from_text method.
    """

    def __init__(self, settings_file: str = "settings.yaml") -> None:
        """Initialize the provider with settings file.

        Args:
            settings_file: Path to the YAML settings file
        """
        self._logger = get_logger(self.__class__.__name__)
        self.settings_file = settings_file
        self.settings = self._load_settings(settings_file)

    def _load_settings(self, settings_file: str) -> Optional[Dict[str, Any]]:
        """Load settings from YAML file.

        Args:
            settings_file: Path to the YAML settings file

        Returns:
            dict: Loaded settings or None if loading fails
        """
        try:
            with open(settings_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self._logger.error(f"Error loading settings file: {e}", exc_info=True)
            return None

    def _build_prompt(self, text: str) -> Optional[str]:
        """Build the prompt from settings and text.

        This method is shared across all providers as they use the same prompt format.

        Args:
            text: The document content to include in the prompt

        Returns:
            str: Complete prompt ready to send to LLM, or None if prompt settings not found
        """
        if not self.settings:
            self._logger.error("Settings not loaded")
            return None

        with_date = self.settings.get("with_date", False)
        setting_prompt = self.settings.get("prompt", None)

        if not setting_prompt:
            self._logger.error("Prompt settings not found")
            return None

        # Build the main prompt
        prompt = setting_prompt.get("main", "")

        # Add date-specific instructions if needed
        if with_date:
            current_date = datetime.today().strftime("%Y-%m-%d")
            with_date_prompt = setting_prompt.get("with_date", "")
            with_date_prompt = with_date_prompt.replace("{current_date}", current_date)
            prompt += with_date_prompt
        else:
            prompt += setting_prompt.get("no_date", "")

        # Add the document content
        prompt += setting_prompt.get("pre_content", "") + text
        prompt += setting_prompt.get("post_content", "")

        return prompt

    def _parse_structured_response(self, content: str) -> Optional[str]:
        """Parse structured JSON response from LLM provider.

        This method is shared across all providers as they use the same
        JSON schema format for structured outputs.

        Args:
            content: JSON string from LLM response

        Returns:
            str: Extracted title, or None if parsing failed
        """
        try:
            # Parse JSON response
            data = json.loads(content)

            # Extract title field
            title = data.get("title", "")

            if not title:
                self._logger.warning(
                    "Structured response missing 'title' field or title is empty. "
                    f"Response: {content}"
                )
                return None

            # Auto-truncate if title exceeds Paperless NGX limit
            if len(title) > MAX_TITLE_LENGTH:
                self._logger.warning(
                    f"Title exceeds {MAX_TITLE_LENGTH} chars, truncating: {title}"
                )
                title = title[:MAX_TITLE_LENGTH]

            return title

        except json.JSONDecodeError as e:
            self._logger.error(
                f"LLM returned invalid JSON: {e}. Content: {content}. "
                "This may indicate the model doesn't support structured outputs."
            )
            return None
        except Exception as e:
            self._logger.error(f"Error parsing structured response: {e}. Content: {content}")
            return None

    @abstractmethod
    def generate_title_from_text(self, text: str) -> Optional[str]:
        """Generate a title from the given text.

        This method must be implemented by all provider subclasses.

        Args:
            text: The document content to generate a title for

        Returns:
            str: Generated title, or None if generation failed
        """
        pass
