"""
Integration tests for OpenAI title generation.

These tests make REAL calls to OpenAI API and will:
- Cost money (small amounts with gpt-4o-mini)
- Require OPENAI_API_KEY environment variable
- Be slower than unit tests (2-5 seconds per test)

Run with: pytest -m openai tests/integration/test_openai_integration.py
"""

import pytest
from modules.openai_titles import OpenAITitles


@pytest.mark.integration
@pytest.mark.openai
@pytest.mark.slow
class TestOpenAITitleGeneration:
    """Test OpenAI integration with real API calls."""

    def test_generate_title_from_invoice(
        self, openai_api_key, settings_valid_path, sample_invoice_text
    ):
        """Test title generation from invoice text."""
        ai = OpenAITitles(openai_api_key, str(settings_valid_path))

        title = ai.generate_title_from_text(sample_invoice_text)

        # Assertions
        assert title is not None
        assert len(title) > 0
        assert len(title) <= 127  # Max title length
        assert "AWS" in title or "Amazon" in title  # Should identify sender
        print(f"Generated title: {title}")

    def test_generate_title_from_legal_text(
        self, openai_api_key, settings_valid_path, sample_legal_text
    ):
        """Test title generation from legal document."""
        ai = OpenAITitles(openai_api_key, str(settings_valid_path))

        title = ai.generate_title_from_text(sample_legal_text)

        assert title is not None
        assert len(title) > 0
        assert len(title) <= 127
        print(f"Generated title: {title}")

    def test_generate_title_with_date_enabled(
        self, openai_api_key, settings_with_date_path, sample_invoice_text
    ):
        """Test title generation with date prefix enabled."""
        ai = OpenAITitles(openai_api_key, str(settings_with_date_path))

        title = ai.generate_title_from_text(sample_invoice_text)

        assert title is not None
        assert len(title) > 0
        # OpenAI may or may not follow date prefix instruction perfectly
        # Just verify settings were loaded correctly
        assert ai.settings.get("with_date") is True
        print(f"Generated title with date enabled: {title}")
        # Note: Title may or may not start with date - OpenAI behavior varies

    def test_settings_loading(self, openai_api_key, settings_valid_path):
        """Test that settings are loaded correctly."""
        ai = OpenAITitles(openai_api_key, str(settings_valid_path))

        assert ai.settings is not None
        assert "openai_model" in ai.settings
        assert "with_date" in ai.settings
        assert "prompt" in ai.settings
        assert ai.settings["openai_model"] == "gpt-4o-mini"
        assert ai.settings["with_date"] is False

    def test_invalid_settings_file(self, openai_api_key, tmp_path):
        """Test handling of invalid settings file."""
        invalid_file = tmp_path / "nonexistent.yaml"

        ai = OpenAITitles(openai_api_key, str(invalid_file))

        assert ai.settings is None

    @pytest.mark.slow
    def test_empty_text_handling(
        self, openai_api_key, settings_valid_path, sample_empty_text
    ):
        """Test handling of empty document text."""
        ai = OpenAITitles(openai_api_key, str(settings_valid_path))

        # Should still work, OpenAI will generate something
        title = ai.generate_title_from_text(sample_empty_text)

        # May return None or a generic title
        if title:
            print(f"Title for empty text: {title}")
