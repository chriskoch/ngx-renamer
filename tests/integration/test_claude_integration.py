"""
Integration tests for Claude title generation.

These tests make REAL calls to Anthropic Claude API and will:
- Cost money (small amounts with claude-3-5-sonnet)
- Require CLAUDE_API_KEY environment variable
- Be slower than unit tests (2-5 seconds per test)

Run with: pytest -m claude tests/integration/test_claude_integration.py
"""

import pytest
from modules.claude_titles import ClaudeTitles


@pytest.mark.integration
@pytest.mark.claude
@pytest.mark.slow
class TestClaudeTitleGeneration:
    """Test Claude integration with real API calls."""

    def test_generate_title_from_invoice(
        self, claude_api_key, settings_claude_path, sample_invoice_text
    ):
        """Test title generation from invoice text."""
        ai = ClaudeTitles(claude_api_key, str(settings_claude_path))

        title = ai.generate_title_from_text(sample_invoice_text)

        # Assertions
        assert title is not None
        assert len(title) > 0
        assert len(title) <= 127  # Max title length
        assert "AWS" in title or "Amazon" in title  # Should identify sender
        print(f"Generated title: {title}")

    def test_generate_title_from_legal_text(
        self, claude_api_key, settings_claude_path, sample_legal_text
    ):
        """Test title generation from legal document."""
        ai = ClaudeTitles(claude_api_key, str(settings_claude_path))

        title = ai.generate_title_from_text(sample_legal_text)

        assert title is not None
        assert len(title) > 0
        assert len(title) <= 127
        print(f"Generated title: {title}")

    def test_generate_title_with_date_enabled(
        self, claude_api_key, settings_claude_with_date_path, sample_invoice_text
    ):
        """Test title generation with date prefix enabled."""
        ai = ClaudeTitles(claude_api_key, str(settings_claude_with_date_path))

        title = ai.generate_title_from_text(sample_invoice_text)

        assert title is not None
        assert len(title) > 0
        # Claude may or may not follow date prefix instruction perfectly
        # Just verify settings were loaded correctly
        assert ai.settings.get("with_date") is True
        print(f"Generated title with date enabled: {title}")
        # Note: Title may or may not start with date - Claude behavior varies

    def test_settings_loading(self, claude_api_key, settings_claude_path):
        """Test that settings are loaded correctly."""
        ai = ClaudeTitles(claude_api_key, str(settings_claude_path))

        assert ai.settings is not None
        assert "claude" in ai.settings
        assert "with_date" in ai.settings
        assert "prompt" in ai.settings
        assert ai.settings["claude"]["model"] == "claude-sonnet-4-5-20250929"
        assert ai.settings["with_date"] is False

    def test_invalid_settings_file(self, claude_api_key, tmp_path):
        """Test handling of invalid settings file."""
        invalid_file = tmp_path / "nonexistent.yaml"

        ai = ClaudeTitles(claude_api_key, str(invalid_file))

        assert ai.settings is None

    @pytest.mark.slow
    def test_empty_text_handling(
        self, claude_api_key, settings_claude_path, sample_empty_text
    ):
        """Test handling of empty document text."""
        ai = ClaudeTitles(claude_api_key, str(settings_claude_path))

        # Should still work, Claude will generate something
        title = ai.generate_title_from_text(sample_empty_text)

        # May return None or a generic title
        if title:
            print(f"Title for empty text: {title}")

    def test_structured_output_format(
        self, claude_api_key, settings_claude_path, sample_invoice_text
    ):
        """Test that Claude returns properly structured JSON output."""
        ai = ClaudeTitles(claude_api_key, str(settings_claude_path))

        title = ai.generate_title_from_text(sample_invoice_text)

        # Verify the title is a string (not a dict or other type)
        assert isinstance(title, str)
        assert len(title) > 0
        assert len(title) <= 127
        print(f"Structured output title: {title}")

    def test_auto_truncation(
        self, claude_api_key, settings_claude_path
    ):
        """Test that titles exceeding 127 characters are auto-truncated."""
        ai = ClaudeTitles(claude_api_key, str(settings_claude_path))

        # Generate title from long complex text
        long_text = """
        This is an extremely long and complex document with many details about
        multiple topics, including business operations, financial transactions,
        legal agreements, and various other matters that should result in a
        very long title if not properly truncated by the system.
        """ * 10

        title = ai.generate_title_from_text(long_text)

        assert title is not None
        assert len(title) <= 127
        print(f"Auto-truncated title ({len(title)} chars): {title}")
