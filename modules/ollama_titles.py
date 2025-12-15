"""Ollama LLM provider for title generation."""
import json
import ollama
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


class OllamaTitles(BaseLLMProvider):
    """Ollama-based title generation provider.

    Uses the Ollama API to generate document titles from text content.
    Requires Ollama to be running locally or accessible via network.
    """

    def __init__(self, ollama_base_url, settings_file="settings.yaml"):
        """Initialize Ollama provider.

        Args:
            ollama_base_url: URL of Ollama API (e.g., http://localhost:11434)
            settings_file: Path to settings.yaml configuration file
        """
        super().__init__(settings_file)
        self.ollama_base_url = ollama_base_url
        self._client = ollama.Client(host=ollama_base_url)

    def __call_ollama_api(self, content, role="user"):
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
                model = self.settings["ollama"].get("model", "gpt-oss:latest")
            else:
                model = "gpt-oss:latest"

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
                model = self.settings.get("ollama", {}).get("model", "gpt-oss:latest")
                print(f"Error: Model '{model}' not found in Ollama.")
                print(f"Please pull the model first: ollama pull {model}")
            else:
                print(f"Error generating title from Ollama (API error): {e}")
            return None
        except Exception as e:
            print(f"Error generating title from Ollama: {e}")
            print(f"Make sure Ollama is running at {self.ollama_base_url}")
            print(f"You can test with: curl {self.ollama_base_url}/api/version")
            return None

    def generate_title_from_text(self, text):
        """Generate a title from text using Ollama.

        Args:
            text: Document content to generate title from

        Returns:
            str: Generated title, or None if generation failed
        """
        prompt = self._build_prompt(text)
        if not prompt:
            return None

        result = self.__call_ollama_api(prompt)
        if result:
            try:
                content = result['message']['content']
                return self._parse_structured_response(content)
            except (KeyError, TypeError) as e:
                print(f"Unexpected response structure from Ollama: {e}")
                print(f"Response: {result}")
                return None

        return None

    def _parse_structured_response(self, content):
        """Parse structured JSON response from Ollama.

        Args:
            content: JSON string from Ollama response

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
            print(f"Error: Ollama returned invalid JSON: {e}")
            print(f"Content: {content}")
            print("This may indicate the model doesn't support structured outputs.")
            return None
        except Exception as e:
            print(f"Error parsing structured response: {e}")
            print(f"Content: {content}")
            return None
