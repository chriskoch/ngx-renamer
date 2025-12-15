"""
Integration tests for Ollama title generation.

These tests make REAL calls to Ollama API and will:
- Require Ollama to be running (default: http://localhost:11434)
- Require the configured model to be pulled (e.g., ollama pull gpt-oss:latest)
- Be slower than unit tests (2-5 seconds per test)
- NOT cost money (runs locally)

Run with: pytest -m ollama tests/integration/test_ollama_integration.py
"""

import pytest
import requests
from modules.ollama_titles import OllamaTitles


def check_ollama_available(ollama_base_url, model="gpt-oss:latest"):
    """Helper to check if Ollama is running and model is available.

    Args:
        ollama_base_url: Base URL of Ollama API
        model: Model name to check

    Returns:
        tuple: (is_available, message)
    """
    try:
        # Check if Ollama is running
        response = requests.get(f"{ollama_base_url}/api/version", timeout=2)
        if response.status_code != 200:
            return False, f"Ollama API not responding at {ollama_base_url}"

        # Check if model is available
        response = requests.get(f"{ollama_base_url}/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            if not any(model in name for name in model_names):
                return False, f"Model '{model}' not found. Run: ollama pull {model}"

        return True, "Ollama is available"
    except requests.exceptions.RequestException as e:
        return False, f"Ollama not running at {ollama_base_url}: {e}"


@pytest.mark.integration
@pytest.mark.ollama
@pytest.mark.slow
class TestOllamaTitleGeneration:
    """Test Ollama integration with real API calls."""

    def test_generate_title_from_invoice(
        self, ollama_base_url, settings_ollama_path, sample_invoice_text
    ):
        """Test title generation from invoice text."""
        # Check if Ollama is available
        available, msg = check_ollama_available(ollama_base_url)
        if not available:
            pytest.skip(msg)

        ai = OllamaTitles(ollama_base_url, str(settings_ollama_path))

        title = ai.generate_title_from_text(sample_invoice_text)

        # Assertions
        assert title is not None
        assert len(title) > 0
        assert len(title) <= 127  # Max title length
        assert "AWS" in title or "Amazon" in title  # Should identify sender
        print(f"Generated title: {title}")

    def test_generate_title_from_legal_text(
        self, ollama_base_url, settings_ollama_path, sample_legal_text
    ):
        """Test title generation from legal document."""
        available, msg = check_ollama_available(ollama_base_url)
        if not available:
            pytest.skip(msg)

        ai = OllamaTitles(ollama_base_url, str(settings_ollama_path))

        title = ai.generate_title_from_text(sample_legal_text)

        assert title is not None
        assert len(title) > 0
        assert len(title) <= 127
        print(f"Generated title: {title}")

    def test_generate_title_with_date_enabled(
        self, ollama_base_url, settings_ollama_with_date_path, sample_invoice_text
    ):
        """Test title generation with date prefix enabled."""
        available, msg = check_ollama_available(ollama_base_url)
        if not available:
            pytest.skip(msg)

        ai = OllamaTitles(ollama_base_url, str(settings_ollama_with_date_path))

        title = ai.generate_title_from_text(sample_invoice_text)

        assert title is not None
        assert len(title) > 0
        # Verify settings were loaded correctly
        assert ai.settings.get("with_date") is True
        print(f"Generated title with date enabled: {title}")

    def test_settings_loading(self, ollama_base_url, settings_ollama_path):
        """Test that settings are loaded correctly."""
        ai = OllamaTitles(ollama_base_url, str(settings_ollama_path))

        assert ai.settings is not None
        assert "ollama" in ai.settings
        assert "with_date" in ai.settings
        assert "prompt" in ai.settings
        assert ai.settings["ollama"]["model"] == "gpt-oss:latest"
        assert ai.settings["with_date"] is False

    def test_invalid_settings_file(self, ollama_base_url, tmp_path):
        """Test handling of invalid settings file."""
        invalid_file = tmp_path / "nonexistent.yaml"

        ai = OllamaTitles(ollama_base_url, str(invalid_file))

        assert ai.settings is None

    @pytest.mark.slow
    def test_empty_text_handling(
        self, ollama_base_url, settings_ollama_path, sample_empty_text
    ):
        """Test handling of empty document text."""
        available, msg = check_ollama_available(ollama_base_url)
        if not available:
            pytest.skip(msg)

        ai = OllamaTitles(ollama_base_url, str(settings_ollama_path))

        # Should still work, Ollama will generate something
        title = ai.generate_title_from_text(sample_empty_text)

        # May return None or a generic title
        if title:
            print(f"Title for empty text: {title}")

    def test_ollama_not_running(self, settings_ollama_path, sample_invoice_text):
        """Test error handling when Ollama is not running."""
        # Use an invalid URL with a port that won't be in use
        invalid_url = "http://localhost:54321"

        ai = OllamaTitles(invalid_url, str(settings_ollama_path))
        title = ai.generate_title_from_text(sample_invoice_text)

        # Should return None when Ollama is not available
        assert title is None

    def test_model_not_found(self, ollama_base_url, tmp_path, sample_invoice_text):
        """Test error handling when model is not pulled."""
        available, msg = check_ollama_available(ollama_base_url)
        if not available:
            pytest.skip("Ollama not running - skipping model not found test")

        # Create settings with a non-existent model
        settings_file = tmp_path / "settings_bad_model.yaml"
        settings_file.write_text("""
llm_provider: "ollama"
with_date: false
ollama:
  model: "nonexistent-model-12345:latest"
prompt:
  main: "Generate a title:\\n\\nDocument text:\\n"
  with_date: ""
  no_date: ""
  pre_content: ""
  post_content: ""
""")

        ai = OllamaTitles(ollama_base_url, str(settings_file))
        title = ai.generate_title_from_text(sample_invoice_text)

        # Should return None when model is not found
        assert title is None

    def test_structured_output_returns_valid_title(
        self, ollama_base_url, settings_ollama_path, sample_invoice_text
    ):
        """Test that structured outputs produce valid titles from real Ollama API."""
        available, msg = check_ollama_available(ollama_base_url)
        if not available:
            pytest.skip(msg)

        ai = OllamaTitles(ollama_base_url, str(settings_ollama_path))
        title = ai.generate_title_from_text(sample_invoice_text)

        # Verify title was generated successfully
        assert title is not None
        assert isinstance(title, str)
        assert len(title) > 0
        assert len(title) <= 127  # Auto-truncation should ensure this
        print(f"Structured output title: {title}")

    def test_structured_output_auto_truncates(
        self, ollama_base_url, settings_ollama_path, sample_long_text
    ):
        """Test that very long documents produce titles within 127 char limit."""
        available, msg = check_ollama_available(ollama_base_url)
        if not available:
            pytest.skip(msg)

        ai = OllamaTitles(ollama_base_url, str(settings_ollama_path))
        title = ai.generate_title_from_text(sample_long_text)

        # Even with very long input, title should be truncated to 127 chars
        assert title is not None
        assert len(title) <= 127
        print(f"Auto-truncated title ({len(title)} chars): {title}")
