"""Anthropic Claude LLM provider for title generation."""
from typing import Optional
import anthropic
from modules.base_llm_provider import BaseLLMProvider
from modules.logger import get_logger
from modules.constants import TITLE_SCHEMA, DEFAULT_MODELS, MAX_TITLE_LENGTH, PROVIDER_CLAUDE


class ClaudeTitles(BaseLLMProvider):
    """Anthropic Claude-based title generation provider.

    Uses the Anthropic Claude API to generate document titles from text content.
    """

    def __init__(self, claude_api_key: str, settings_file: str = "settings.yaml") -> None:
        """Initialize Claude provider.

        Args:
            claude_api_key: Anthropic API key for authentication
            settings_file: Path to settings.yaml configuration file
        """
        super().__init__(settings_file)
        self._claude_client = anthropic.Anthropic(api_key=claude_api_key)

    def _call_claude_api(self, content: str) -> Optional[anthropic.types.Message]:
        """Call Claude messages API.

        Args:
            content: The prompt/content to send to Claude

        Returns:
            Claude response object, or None on error
        """
        try:
            # Support both new and legacy settings structure
            # New structure: settings["claude"]["model"]
            # Legacy structure: settings["claude_model"]
            if "claude" in self.settings and isinstance(self.settings["claude"], dict):
                model = self.settings["claude"].get("model", DEFAULT_MODELS[PROVIDER_CLAUDE])
            else:
                # Backward compatibility - check root level
                model = self.settings.get("claude_model", DEFAULT_MODELS[PROVIDER_CLAUDE])

            # Use JSON mode for structured outputs
            # Claude supports tool use for structured outputs
            response = self._claude_client.messages.create(
                model=model,
                max_tokens=1024,
                tools=[
                    {
                        "name": "document_title",
                        "description": "Generate a concise, descriptive title for a document",
                        "input_schema": TITLE_SCHEMA
                    }
                ],
                tool_choice={"type": "tool", "name": "document_title"},
                messages=[
                    {
                        "role": "user",
                        "content": content
                    }
                ]
            )
            return response
        except anthropic.APIError as e:
            self._logger.error(f"Claude API error: {e}")
            return None
        except Exception as e:
            self._logger.error(f"Error generating title from Claude: {e}")
            return None

    def generate_title_from_text(self, text: str) -> Optional[str]:
        """Generate a title from text using Claude.

        Args:
            text: Document content to generate title from

        Returns:
            str: Generated title, or None if generation failed
        """
        prompt = self._build_prompt(text)
        if not prompt:
            return None

        result = self._call_claude_api(prompt)
        if result:
            try:
                # Extract tool use result from Claude response
                for block in result.content:
                    if block.type == "tool_use" and block.name == "document_title":
                        # Claude returns the structured data directly
                        title = block.input.get("title", "")
                        if not title:
                            self._logger.warning("Claude returned empty title")
                            return None
                        # Ensure title doesn't exceed max length
                        if len(title) > MAX_TITLE_LENGTH:
                            self._logger.warning(f"Title exceeds {MAX_TITLE_LENGTH} chars, truncating...")
                            title = title[:MAX_TITLE_LENGTH]
                        return title

                self._logger.error("No tool_use block found in Claude response")
                return None
            except (AttributeError, KeyError, TypeError) as e:
                self._logger.error(f"Unexpected response structure from Claude: {e}")
                self._logger.error(f"Response: {result}")
                return None

        return None
