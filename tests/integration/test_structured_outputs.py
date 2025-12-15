"""
Unit tests for structured output parsing in both Ollama and OpenAI providers.

Tests the _parse_structured_response() method for:
- Valid JSON parsing
- Auto-truncation of titles > 127 chars
- Invalid JSON handling
- Missing 'title' field
- Empty titles
- Schema structure validation
"""

import json
import pytest
from modules.ollama_titles import OllamaTitles, TITLE_SCHEMA as OLLAMA_SCHEMA
from modules.openai_titles import OpenAITitles, TITLE_SCHEMA as OPENAI_SCHEMA


class TestSchemaStructure:
    """Test that JSON schemas are correctly formatted."""

    def test_ollama_schema_structure(self):
        """Verify Ollama JSON schema is correctly formatted."""
        assert "type" in OLLAMA_SCHEMA
        assert OLLAMA_SCHEMA["type"] == "object"
        assert "properties" in OLLAMA_SCHEMA
        assert "title" in OLLAMA_SCHEMA["properties"]
        assert OLLAMA_SCHEMA["properties"]["title"]["type"] == "string"
        assert OLLAMA_SCHEMA["properties"]["title"]["maxLength"] == 127
        assert OLLAMA_SCHEMA["required"] == ["title"]
        assert OLLAMA_SCHEMA["additionalProperties"] is False

    def test_openai_schema_structure(self):
        """Verify OpenAI JSON schema is correctly formatted."""
        assert "type" in OPENAI_SCHEMA
        assert OPENAI_SCHEMA["type"] == "object"
        assert "properties" in OPENAI_SCHEMA
        assert "title" in OPENAI_SCHEMA["properties"]
        assert OPENAI_SCHEMA["properties"]["title"]["type"] == "string"
        assert OPENAI_SCHEMA["properties"]["title"]["maxLength"] == 127
        assert OPENAI_SCHEMA["required"] == ["title"]
        assert OPENAI_SCHEMA["additionalProperties"] is False

    def test_schemas_are_identical(self):
        """Verify both providers use the same schema."""
        assert OLLAMA_SCHEMA == OPENAI_SCHEMA


class TestOllamaStructuredOutputParsing:
    """Test Ollama structured JSON response parsing."""

    def test_parse_valid_json(self, settings_ollama_path, ollama_base_url):
        """Test parsing valid structured JSON response."""
        ai = OllamaTitles(ollama_base_url, str(settings_ollama_path))

        json_response = '{"title": "Amazon - Monthly Subscription Invoice"}'
        title = ai._parse_structured_response(json_response)

        assert title == "Amazon - Monthly Subscription Invoice"

    def test_parse_title_with_special_characters(self, settings_ollama_path, ollama_base_url):
        """Test parsing titles with special characters."""
        ai = OllamaTitles(ollama_base_url, str(settings_ollama_path))

        json_response = '{"title": "Invoice #12345 - Payment €150.00 (2024-01-15)"}'
        title = ai._parse_structured_response(json_response)

        assert title == "Invoice #12345 - Payment €150.00 (2024-01-15)"

    def test_parse_title_exactly_127_chars(self, settings_ollama_path, ollama_base_url):
        """Test that titles with exactly 127 chars are not truncated."""
        ai = OllamaTitles(ollama_base_url, str(settings_ollama_path))

        title_127 = "A" * 127
        json_response = json.dumps({"title": title_127})
        title = ai._parse_structured_response(json_response)

        assert title == title_127
        assert len(title) == 127

    def test_parse_title_too_long(self, settings_ollama_path, ollama_base_url):
        """Test that titles exceeding 127 chars are auto-truncated."""
        ai = OllamaTitles(ollama_base_url, str(settings_ollama_path))

        long_title = "A" * 150
        json_response = json.dumps({"title": long_title})
        title = ai._parse_structured_response(json_response)

        assert title is not None
        assert len(title) == 127
        assert title == "A" * 127

    def test_parse_title_unicode_truncation(self, settings_ollama_path, ollama_base_url):
        """Test truncation with Unicode characters."""
        ai = OllamaTitles(ollama_base_url, str(settings_ollama_path))

        # Create a title with emojis that exceeds 127 chars
        long_title = "Invoice 📄 " * 20  # This will be > 127 chars
        json_response = json.dumps({"title": long_title})
        title = ai._parse_structured_response(json_response)

        assert title is not None
        assert len(title) == 127

    def test_parse_invalid_json(self, settings_ollama_path, ollama_base_url):
        """Test handling of invalid JSON."""
        ai = OllamaTitles(ollama_base_url, str(settings_ollama_path))

        invalid_json = "This is not JSON at all"
        title = ai._parse_structured_response(invalid_json)

        assert title is None

    def test_parse_malformed_json(self, settings_ollama_path, ollama_base_url):
        """Test handling of malformed JSON."""
        ai = OllamaTitles(ollama_base_url, str(settings_ollama_path))

        malformed_json = '{"title": "Missing closing brace"'
        title = ai._parse_structured_response(malformed_json)

        assert title is None

    def test_parse_missing_title_field(self, settings_ollama_path, ollama_base_url):
        """Test handling of JSON missing 'title' field."""
        ai = OllamaTitles(ollama_base_url, str(settings_ollama_path))

        json_response = '{"wrong_field": "Some value"}'
        title = ai._parse_structured_response(json_response)

        assert title is None

    def test_parse_empty_title(self, settings_ollama_path, ollama_base_url):
        """Test handling of empty title string."""
        ai = OllamaTitles(ollama_base_url, str(settings_ollama_path))

        json_response = '{"title": ""}'
        title = ai._parse_structured_response(json_response)

        assert title is None

    def test_parse_null_title(self, settings_ollama_path, ollama_base_url):
        """Test handling of null title value."""
        ai = OllamaTitles(ollama_base_url, str(settings_ollama_path))

        json_response = '{"title": null}'
        title = ai._parse_structured_response(json_response)

        assert title is None

    def test_parse_whitespace_only_title(self, settings_ollama_path, ollama_base_url):
        """Test handling of whitespace-only title."""
        ai = OllamaTitles(ollama_base_url, str(settings_ollama_path))

        json_response = '{"title": "   "}'
        title = ai._parse_structured_response(json_response)

        # Whitespace-only titles should pass through (valid but unusual)
        assert title == "   "

    def test_parse_json_with_extra_fields(self, settings_ollama_path, ollama_base_url):
        """Test parsing JSON with extra fields (should work despite additionalProperties: false)."""
        ai = OllamaTitles(ollama_base_url, str(settings_ollama_path))

        json_response = '{"title": "Test Title", "extra_field": "ignored", "another": 123}'
        title = ai._parse_structured_response(json_response)

        assert title == "Test Title"


class TestOpenAIStructuredOutputParsing:
    """Test OpenAI structured JSON response parsing."""

    def test_parse_valid_json(self, settings_openai_new_format_path, openai_api_key):
        """Test parsing valid structured JSON response."""
        ai = OpenAITitles(openai_api_key, str(settings_openai_new_format_path))

        json_response = '{"title": "Legal Document - Contract Review"}'
        title = ai._parse_structured_response(json_response)

        assert title == "Legal Document - Contract Review"

    def test_parse_title_with_special_characters(self, settings_openai_new_format_path, openai_api_key):
        """Test parsing titles with special characters."""
        ai = OpenAITitles(openai_api_key, str(settings_openai_new_format_path))

        json_response = '{"title": "Q&A Session - R&D Meeting (10/15)"}'
        title = ai._parse_structured_response(json_response)

        assert title == "Q&A Session - R&D Meeting (10/15)"

    def test_parse_title_exactly_127_chars(self, settings_openai_new_format_path, openai_api_key):
        """Test that titles with exactly 127 chars are not truncated."""
        ai = OpenAITitles(openai_api_key, str(settings_openai_new_format_path))

        title_127 = "B" * 127
        json_response = json.dumps({"title": title_127})
        title = ai._parse_structured_response(json_response)

        assert title == title_127
        assert len(title) == 127

    def test_parse_title_too_long(self, settings_openai_new_format_path, openai_api_key):
        """Test that titles exceeding 127 chars are auto-truncated."""
        ai = OpenAITitles(openai_api_key, str(settings_openai_new_format_path))

        long_title = "B" * 200
        json_response = json.dumps({"title": long_title})
        title = ai._parse_structured_response(json_response)

        assert title is not None
        assert len(title) == 127
        assert title == "B" * 127

    def test_parse_invalid_json(self, settings_openai_new_format_path, openai_api_key):
        """Test handling of invalid JSON."""
        ai = OpenAITitles(openai_api_key, str(settings_openai_new_format_path))

        invalid_json = "Plain text title without JSON"
        title = ai._parse_structured_response(invalid_json)

        assert title is None

    def test_parse_malformed_json(self, settings_openai_new_format_path, openai_api_key):
        """Test handling of malformed JSON."""
        ai = OpenAITitles(openai_api_key, str(settings_openai_new_format_path))

        malformed_json = '{"title": "Unclosed quote}'
        title = ai._parse_structured_response(malformed_json)

        assert title is None

    def test_parse_missing_title_field(self, settings_openai_new_format_path, openai_api_key):
        """Test handling of JSON missing 'title' field."""
        ai = OpenAITitles(openai_api_key, str(settings_openai_new_format_path))

        json_response = '{"document_title": "Wrong field name"}'
        title = ai._parse_structured_response(json_response)

        assert title is None

    def test_parse_empty_title(self, settings_openai_new_format_path, openai_api_key):
        """Test handling of empty title string."""
        ai = OpenAITitles(openai_api_key, str(settings_openai_new_format_path))

        json_response = '{"title": ""}'
        title = ai._parse_structured_response(json_response)

        assert title is None

    def test_parse_null_title(self, settings_openai_new_format_path, openai_api_key):
        """Test handling of null title value."""
        ai = OpenAITitles(openai_api_key, str(settings_openai_new_format_path))

        json_response = '{"title": null}'
        title = ai._parse_structured_response(json_response)

        assert title is None

    def test_parse_json_with_extra_fields(self, settings_openai_new_format_path, openai_api_key):
        """Test parsing JSON with extra fields."""
        ai = OpenAITitles(openai_api_key, str(settings_openai_new_format_path))

        json_response = '{"title": "Test Title", "confidence": 0.95, "language": "en"}'
        title = ai._parse_structured_response(json_response)

        assert title == "Test Title"


class TestCrossProviderConsistency:
    """Test that both providers handle edge cases consistently."""

    def test_both_providers_truncate_identically(self, settings_ollama_path, settings_openai_new_format_path,
                                                   ollama_base_url, openai_api_key):
        """Verify both providers truncate long titles to exactly 127 chars."""
        ollama_ai = OllamaTitles(ollama_base_url, str(settings_ollama_path))
        openai_ai = OpenAITitles(openai_api_key, str(settings_openai_new_format_path))

        long_title = "X" * 150
        json_response = json.dumps({"title": long_title})

        ollama_result = ollama_ai._parse_structured_response(json_response)
        openai_result = openai_ai._parse_structured_response(json_response)

        assert ollama_result == openai_result
        assert len(ollama_result) == 127
        assert len(openai_result) == 127

    def test_both_providers_handle_invalid_json_identically(self, settings_ollama_path,
                                                             settings_openai_new_format_path,
                                                             ollama_base_url, openai_api_key):
        """Verify both providers return None for invalid JSON."""
        ollama_ai = OllamaTitles(ollama_base_url, str(settings_ollama_path))
        openai_ai = OpenAITitles(openai_api_key, str(settings_openai_new_format_path))

        invalid_json = "Not valid JSON"

        ollama_result = ollama_ai._parse_structured_response(invalid_json)
        openai_result = openai_ai._parse_structured_response(invalid_json)

        assert ollama_result is None
        assert openai_result is None

    def test_both_providers_handle_missing_field_identically(self, settings_ollama_path,
                                                               settings_openai_new_format_path,
                                                               ollama_base_url, openai_api_key):
        """Verify both providers return None for missing 'title' field."""
        ollama_ai = OllamaTitles(ollama_base_url, str(settings_ollama_path))
        openai_ai = OpenAITitles(openai_api_key, str(settings_openai_new_format_path))

        json_response = '{"wrong_field": "value"}'

        ollama_result = ollama_ai._parse_structured_response(json_response)
        openai_result = openai_ai._parse_structured_response(json_response)

        assert ollama_result is None
        assert openai_result is None
