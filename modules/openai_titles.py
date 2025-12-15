import json
from openai import OpenAI
from modules.base_llm_provider import BaseLLMProvider


# JSON schema for structured title output
TITLE_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "maxLength": 128,
            "description": "The generated document title"
        }
    },
    "required": ["title"],
    "additionalProperties": False
}


class OpenAITitles(BaseLLMProvider):
    """OpenAI-based title generation provider.

    Uses the OpenAI API to generate document titles from text content.
    """

    def __init__(self, openai_api_key, settings_file="settings.yaml"):
        """Initialize OpenAI provider.

        Args:
            openai_api_key: OpenAI API key for authentication
            settings_file: Path to settings.yaml configuration file
        """
        super().__init__(settings_file)
        self.__openai = OpenAI(api_key=openai_api_key)

    def __call_openai_api(self, content, role="user"):
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
                model = self.settings["openai"].get("model", "gpt-4o-mini")
            else:
                # Backward compatibility - check root level
                model = self.settings.get("openai_model", "gpt-4o-mini")

            res = self.__openai.chat.completions.create(
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
            print(f"Error generating title from GPT: {e}")
            return None

    def generate_title_from_text(self, text):
        """Generate a title from text using OpenAI.

        Args:
            text: Document content to generate title from

        Returns:
            str: Generated title, or None if generation failed
        """
        prompt = self._build_prompt(text)
        if not prompt:
            return None

        result = self.__call_openai_api(prompt)
        if result:
            content = result.choices[0].message.content
            return self._parse_structured_response(content)

        return None

    def _parse_structured_response(self, content):
        """Parse structured JSON response from OpenAI.

        Args:
            content: JSON string from OpenAI response

        Returns:
            str: Extracted title, or None if parsing failed
        """
        try:
            # Parse JSON response
            data = json.loads(content)

            # Extract title field
            title = data.get("title", "")

            if not title:
                print("Warning: Structured response missing 'title' field or title is empty")
                print(f"Response: {content}")
                return None

            # Auto-truncate if title exceeds Paperless NGX limit (127 chars)
            if len(title) > 127:
                print(f"Warning: Title exceeds 127 chars, truncating: {title}")
                title = title[:127]

            return title

        except json.JSONDecodeError as e:
            print(f"Error: OpenAI returned invalid JSON: {e}")
            print(f"Content: {content}")
            print("This may indicate the model doesn't support structured outputs.")
            return None
        except Exception as e:
            print(f"Error parsing structured response: {e}")
            print(f"Content: {content}")
            return None
    
