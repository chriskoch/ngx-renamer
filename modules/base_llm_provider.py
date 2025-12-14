"""Base abstract class for LLM providers in ngx-renamer."""
from abc import ABC, abstractmethod
from datetime import datetime
import yaml


class BaseLLMProvider(ABC):
    """Abstract base class for LLM title generation providers.

    All LLM providers (OpenAI, Ollama, etc.) must inherit from this class
    and implement the generate_title_from_text method.
    """

    def __init__(self, settings_file="settings.yaml"):
        """Initialize the provider with settings file.

        Args:
            settings_file: Path to the YAML settings file
        """
        self.settings_file = settings_file
        self.settings = self._load_settings(settings_file)

    def _load_settings(self, settings_file):
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
            print(f"Error loading settings file: {e}")
            return None

    def _build_prompt(self, text):
        """Build the prompt from settings and text.

        This method is shared across all providers as they use the same prompt format.

        Args:
            text: The document content to include in the prompt

        Returns:
            str: Complete prompt ready to send to LLM, or None if prompt settings not found
        """
        if not self.settings:
            print("Settings not loaded.")
            return None

        with_date = self.settings.get("with_date", False)
        setting_prompt = self.settings.get("prompt", None)

        if not setting_prompt:
            print("Prompt settings not found.")
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

    @abstractmethod
    def generate_title_from_text(self, text):
        """Generate a title from the given text.

        This method must be implemented by all provider subclasses.

        Args:
            text: The document content to generate a title for

        Returns:
            str: Generated title, or None if generation failed
        """
        pass
