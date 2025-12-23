"""
Tests for multi-LLM provider selection and factory pattern.

These tests verify that:
- The correct LLM provider is selected based on settings
- Provider initialization handles missing credentials correctly
- Invalid providers are rejected with clear error messages
- Both OpenAI and Ollama providers can be instantiated correctly

These are unit/integration hybrid tests - they test the factory logic
but may skip actual API calls if credentials/services are not available.

Run with: pytest tests/integration/test_llm_provider_selection.py
"""

import pytest
from modules.paperless_ai_titles import PaperlessAITitles
from modules.openai_titles import OpenAITitles
from modules.ollama_titles import OllamaTitles
from modules.claude_titles import ClaudeTitles


@pytest.mark.integration
class TestLLMProviderSelection:
    """Test the LLM provider factory and selection logic."""

    def test_select_openai_provider_with_new_format(
        self,
        openai_api_key,
        settings_openai_new_format_path,
        paperless_url,
        paperless_api_key,
    ):
        """Test that OpenAI provider is selected when llm_provider='openai'."""
        ai_titles = PaperlessAITitles(
            openai_api_key=openai_api_key,
            ollama_base_url=None,
            paperless_url=paperless_url,
            paperless_api_key=paperless_api_key,
            settings_file=str(settings_openai_new_format_path),
        )

        # Verify correct provider was instantiated
        assert isinstance(ai_titles.ai, OpenAITitles)
        assert ai_titles.settings.get("llm_provider") == "openai"
        assert ai_titles.settings.get("openai", {}).get("model") == "gpt-4o-mini"

    def test_select_ollama_provider(
        self,
        ollama_base_url,
        settings_ollama_path,
        paperless_url,
        paperless_api_key,
    ):
        """Test that Ollama provider is selected when llm_provider='ollama'."""
        ai_titles = PaperlessAITitles(
            openai_api_key=None,
            ollama_base_url=ollama_base_url,
            paperless_url=paperless_url,
            paperless_api_key=paperless_api_key,
            settings_file=str(settings_ollama_path),
        )

        # Verify correct provider was instantiated
        assert isinstance(ai_titles.ai, OllamaTitles)
        assert ai_titles.settings.get("llm_provider") == "ollama"
        assert ai_titles.settings.get("ollama", {}).get("model") == "gpt-oss:latest"

    def test_select_claude_provider(
        self,
        claude_api_key,
        settings_claude_path,
        paperless_url,
        paperless_api_key,
    ):
        """Test that Claude provider is selected when llm_provider='claude'."""
        ai_titles = PaperlessAITitles(
            openai_api_key=None,
            ollama_base_url=None,
            claude_api_key=claude_api_key,
            paperless_url=paperless_url,
            paperless_api_key=paperless_api_key,
            settings_file=str(settings_claude_path),
        )

        # Verify correct provider was instantiated
        assert isinstance(ai_titles.ai, ClaudeTitles)
        assert ai_titles.settings.get("llm_provider") == "claude"
        assert ai_titles.settings.get("claude", {}).get("model") == "claude-sonnet-4-5-20250929"

    def test_missing_openai_api_key(
        self,
        settings_openai_new_format_path,
        paperless_url,
        paperless_api_key,
    ):
        """Test error when OpenAI is selected but API key is missing."""
        with pytest.raises(ValueError) as exc_info:
            PaperlessAITitles(
                openai_api_key=None,  # Missing API key
                ollama_base_url=None,
                paperless_url=paperless_url,
                paperless_api_key=paperless_api_key,
                settings_file=str(settings_openai_new_format_path),
            )

        error_message = str(exc_info.value)
        assert "OPENAI_API_KEY" in error_message
        assert "required" in error_message.lower()

    def test_missing_ollama_base_url(
        self,
        settings_ollama_path,
        paperless_url,
        paperless_api_key,
    ):
        """Test error when Ollama is selected but base URL is missing."""
        with pytest.raises(ValueError) as exc_info:
            PaperlessAITitles(
                openai_api_key=None,
                ollama_base_url=None,  # Missing base URL
                paperless_url=paperless_url,
                paperless_api_key=paperless_api_key,
                settings_file=str(settings_ollama_path),
            )

        error_message = str(exc_info.value)
        assert "OLLAMA_BASE_URL" in error_message
        assert "required" in error_message.lower()

    def test_missing_claude_api_key(
        self,
        settings_claude_path,
        paperless_url,
        paperless_api_key,
    ):
        """Test error when Claude is selected but API key is missing."""
        with pytest.raises(ValueError) as exc_info:
            PaperlessAITitles(
                openai_api_key=None,
                ollama_base_url=None,
                claude_api_key=None,  # Missing API key
                paperless_url=paperless_url,
                paperless_api_key=paperless_api_key,
                settings_file=str(settings_claude_path),
            )

        error_message = str(exc_info.value)
        assert "CLAUDE_API_KEY" in error_message
        assert "required" in error_message.lower()

    def test_invalid_provider(
        self,
        settings_invalid_provider_path,
        paperless_url,
        paperless_api_key,
    ):
        """Test error when an invalid provider is specified."""
        with pytest.raises(ValueError) as exc_info:
            PaperlessAITitles(
                openai_api_key="fake-key",
                ollama_base_url="http://localhost:11434",
                paperless_url=paperless_url,
                paperless_api_key=paperless_api_key,
                settings_file=str(settings_invalid_provider_path),
            )

        error_message = str(exc_info.value)
        assert "Unknown LLM provider" in error_message
        assert "invalid_provider" in error_message

    def test_backward_compatibility_default_to_openai(
        self,
        openai_api_key,
        settings_valid_path,  # Old format without llm_provider
        paperless_url,
        paperless_api_key,
    ):
        """Test that old settings without llm_provider default to OpenAI."""
        ai_titles = PaperlessAITitles(
            openai_api_key=openai_api_key,
            ollama_base_url=None,
            paperless_url=paperless_url,
            paperless_api_key=paperless_api_key,
            settings_file=str(settings_valid_path),
        )

        # Should default to OpenAI for backward compatibility
        assert isinstance(ai_titles.ai, OpenAITitles)

    def test_provider_case_insensitive(
        self,
        openai_api_key,
        tmp_path,
        paperless_url,
        paperless_api_key,
    ):
        """Test that provider names are case-insensitive."""
        # Create settings with uppercase provider
        settings_file = tmp_path / "settings_uppercase.yaml"
        settings_file.write_text("""
llm_provider: "OPENAI"
openai:
  model: "gpt-4o-mini"
with_date: false
prompt:
  main: "Generate a title:\\n"
  with_date: ""
  no_date: ""
  pre_content: ""
  post_content: ""
""")

        ai_titles = PaperlessAITitles(
            openai_api_key=openai_api_key,
            ollama_base_url=None,
            paperless_url=paperless_url,
            paperless_api_key=paperless_api_key,
            settings_file=str(settings_file),
        )

        assert isinstance(ai_titles.ai, OpenAITitles)


@pytest.mark.integration
@pytest.mark.slow
class TestMultiProviderEndToEnd:
    """End-to-end tests comparing OpenAI and Ollama providers."""

    def test_both_providers_generate_titles(
        self,
        openai_api_key,
        ollama_base_url,
        settings_openai_new_format_path,
        settings_ollama_path,
        paperless_url,
        paperless_api_key,
        sample_invoice_text,
    ):
        """Test that both providers can generate titles from the same text.

        This test requires both OpenAI API key and Ollama to be running.
        """
        # Test OpenAI
        openai_titles = PaperlessAITitles(
            openai_api_key=openai_api_key,
            ollama_base_url=None,
            paperless_url=paperless_url,
            paperless_api_key=paperless_api_key,
            settings_file=str(settings_openai_new_format_path),
        )

        openai_title = openai_titles.ai.generate_title_from_text(sample_invoice_text)

        # Skip Ollama test if not available
        try:
            import requests
            response = requests.get(f"{ollama_base_url}/api/version", timeout=2)
            if response.status_code != 200:
                pytest.skip(f"Ollama not running at {ollama_base_url}")
        except Exception:
            pytest.skip(f"Ollama not running at {ollama_base_url}")

        # Test Ollama
        ollama_titles = PaperlessAITitles(
            openai_api_key=None,
            ollama_base_url=ollama_base_url,
            paperless_url=paperless_url,
            paperless_api_key=paperless_api_key,
            settings_file=str(settings_ollama_path),
        )

        ollama_title = ollama_titles.ai.generate_title_from_text(sample_invoice_text)

        # Both should produce valid titles
        assert openai_title is not None
        assert ollama_title is not None
        assert len(openai_title) > 0
        assert len(ollama_title) > 0
        assert len(openai_title) <= 127
        assert len(ollama_title) <= 127

        # Both should identify it's from Amazon/AWS
        assert "AWS" in openai_title or "Amazon" in openai_title
        assert "AWS" in ollama_title or "Amazon" in ollama_title

        print(f"OpenAI title: {openai_title}")
        print(f"Ollama title: {ollama_title}")

    def test_switching_providers_at_runtime(
        self,
        openai_api_key,
        ollama_base_url,
        settings_openai_new_format_path,
        settings_ollama_path,
        paperless_url,
        paperless_api_key,
        sample_legal_text,
    ):
        """Test switching between providers with different settings files."""
        # Start with OpenAI
        ai_titles = PaperlessAITitles(
            openai_api_key=openai_api_key,
            ollama_base_url=ollama_base_url,
            paperless_url=paperless_url,
            paperless_api_key=paperless_api_key,
            settings_file=str(settings_openai_new_format_path),
        )

        assert isinstance(ai_titles.ai, OpenAITitles)

        # Create new instance with Ollama settings
        ai_titles_ollama = PaperlessAITitles(
            openai_api_key=openai_api_key,
            ollama_base_url=ollama_base_url,
            paperless_url=paperless_url,
            paperless_api_key=paperless_api_key,
            settings_file=str(settings_ollama_path),
        )

        assert isinstance(ai_titles_ollama.ai, OllamaTitles)

        # Verify they use different providers
        assert type(ai_titles.ai) != type(ai_titles_ollama.ai)
