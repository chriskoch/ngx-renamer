"""
Tests for Ollama API key authentication (commit 133d32b).

These tests verify that:
- OllamaTitles works with API key (sets Authorization header)
- OllamaTitles works without API key (no Authorization header)
- OllamaTitles handles empty/whitespace API keys correctly
- PaperlessAITitles passes API key correctly to OllamaTitles
- Integration tests verify actual API calls work with and without API key

Run with: pytest tests/integration/test_ollama_api_key.py
"""

import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from modules.ollama_titles import OllamaTitles
from modules.paperless_ai_titles import PaperlessAITitles


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
class TestOllamaAPIKeyInitialization:
    """Test OllamaTitles initialization with and without API key."""

    def test_init_with_api_key(self, ollama_base_url, settings_ollama_path):
        """Test that OllamaTitles initializes correctly with API key."""
        api_key = "test-api-key-12345"
        ai = OllamaTitles(ollama_base_url, api_key=api_key, settings_file=str(settings_ollama_path))

        # Verify API key is stored
        assert ai.api_key == api_key
        assert ai.ollama_base_url == ollama_base_url

        # Verify client was created (we can't easily check headers without mocking)
        assert ai._client is not None

    def test_init_without_api_key(self, ollama_base_url, settings_ollama_path):
        """Test that OllamaTitles initializes correctly without API key."""
        ai = OllamaTitles(ollama_base_url, api_key=None, settings_file=str(settings_ollama_path))

        # Verify API key is None
        assert ai.api_key is None
        assert ai.ollama_base_url == ollama_base_url
        assert ai._client is not None

    def test_init_with_empty_api_key(self, ollama_base_url, settings_ollama_path):
        """Test that OllamaTitles handles empty API key correctly."""
        ai = OllamaTitles(ollama_base_url, api_key="", settings_file=str(settings_ollama_path))

        # Empty string should be treated as no API key
        assert ai.api_key == ""
        assert ai._client is not None

    def test_init_with_whitespace_api_key(self, ollama_base_url, settings_ollama_path):
        """Test that OllamaTitles handles whitespace-only API key correctly."""
        ai = OllamaTitles(ollama_base_url, api_key="   ", settings_file=str(settings_ollama_path))

        # Whitespace-only string should be treated as no API key
        assert ai.api_key == "   "
        assert ai._client is not None

    @patch('modules.ollama_titles.ollama.Client')
    def test_api_key_sets_authorization_header(self, mock_client_class, ollama_base_url, settings_ollama_path):
        """Test that API key sets Authorization header in Ollama client."""
        api_key = "test-api-key-12345"
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        ai = OllamaTitles(ollama_base_url, api_key=api_key, settings_file=str(settings_ollama_path))

        # Verify Client was called with correct headers
        mock_client_class.assert_called_once()
        call_kwargs = mock_client_class.call_args[1]
        assert call_kwargs['host'] == ollama_base_url
        assert 'headers' in call_kwargs
        assert call_kwargs['headers']['Authorization'] == f"Bearer {api_key}"

    @patch('modules.ollama_titles.ollama.Client')
    def test_no_api_key_no_authorization_header(self, mock_client_class, ollama_base_url, settings_ollama_path):
        """Test that no API key means no Authorization header."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        ai = OllamaTitles(ollama_base_url, api_key=None, settings_file=str(settings_ollama_path))

        # Verify Client was called without Authorization header
        mock_client_class.assert_called_once()
        call_kwargs = mock_client_class.call_args[1]
        assert call_kwargs['host'] == ollama_base_url
        assert 'headers' in call_kwargs
        assert call_kwargs['headers'] == {}  # Empty headers dict

    @patch('modules.ollama_titles.ollama.Client')
    def test_empty_api_key_no_authorization_header(self, mock_client_class, ollama_base_url, settings_ollama_path):
        """Test that empty API key doesn't set Authorization header."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        ai = OllamaTitles(ollama_base_url, api_key="", settings_file=str(settings_ollama_path))

        # Verify Client was called without Authorization header
        mock_client_class.assert_called_once()
        call_kwargs = mock_client_class.call_args[1]
        assert call_kwargs['host'] == ollama_base_url
        assert 'headers' in call_kwargs
        assert call_kwargs['headers'] == {}  # Empty headers dict

    @patch('modules.ollama_titles.ollama.Client')
    def test_whitespace_api_key_no_authorization_header(self, mock_client_class, ollama_base_url, settings_ollama_path):
        """Test that whitespace-only API key doesn't set Authorization header."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        ai = OllamaTitles(ollama_base_url, api_key="   ", settings_file=str(settings_ollama_path))

        # Verify Client was called without Authorization header
        mock_client_class.assert_called_once()
        call_kwargs = mock_client_class.call_args[1]
        assert call_kwargs['host'] == ollama_base_url
        assert 'headers' in call_kwargs
        assert call_kwargs['headers'] == {}  # Empty headers dict


@pytest.mark.integration
class TestPaperlessAITitlesAPIKeyPassing:
    """Test that PaperlessAITitles correctly passes API key to OllamaTitles."""

    def test_paperless_passes_api_key_to_ollama(
        self,
        ollama_base_url,
        settings_ollama_path,
        paperless_url,
        paperless_api_key,
    ):
        """Test that PaperlessAITitles passes API key to OllamaTitles."""
        ollama_api_key = "test-ollama-api-key-12345"

        with patch('modules.ollama_titles.ollama.Client') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            ai_titles = PaperlessAITitles(
                openai_api_key=None,
                ollama_base_url=ollama_base_url,
                ollama_api_key=ollama_api_key,
                paperless_url=paperless_url,
                paperless_api_key=paperless_api_key,
                settings_file=str(settings_ollama_path),
            )

            # Verify OllamaTitles was created with API key
            assert isinstance(ai_titles.ai, OllamaTitles)
            assert ai_titles.ai.api_key == ollama_api_key

            # Verify Client was called with Authorization header
            mock_client_class.assert_called_once()
            call_kwargs = mock_client_class.call_args[1]
            assert call_kwargs['headers']['Authorization'] == f"Bearer {ollama_api_key}"

    def test_paperless_passes_none_api_key_to_ollama(
        self,
        ollama_base_url,
        settings_ollama_path,
        paperless_url,
        paperless_api_key,
    ):
        """Test that PaperlessAITitles passes None API key to OllamaTitles."""
        with patch('modules.ollama_titles.ollama.Client') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            ai_titles = PaperlessAITitles(
                openai_api_key=None,
                ollama_base_url=ollama_base_url,
                ollama_api_key=None,
                paperless_url=paperless_url,
                paperless_api_key=paperless_api_key,
                settings_file=str(settings_ollama_path),
            )

            # Verify OllamaTitles was created without API key
            assert isinstance(ai_titles.ai, OllamaTitles)
            assert ai_titles.ai.api_key is None

            # Verify Client was called without Authorization header
            mock_client_class.assert_called_once()
            call_kwargs = mock_client_class.call_args[1]
            assert call_kwargs['headers'] == {}


@pytest.mark.integration
@pytest.mark.ollama
@pytest.mark.slow
class TestOllamaAPIKeyIntegration:
    """Integration tests for Ollama API key with real API calls."""

    def test_generate_title_without_api_key(
        self,
        ollama_base_url,
        settings_ollama_path,
        sample_invoice_text,
    ):
        """Test that title generation works without API key (local Ollama)."""
        # Check if Ollama is available
        available, msg = check_ollama_available(ollama_base_url)
        if not available:
            pytest.skip(msg)

        # Create OllamaTitles without API key
        ai = OllamaTitles(ollama_base_url, api_key=None, settings_file=str(settings_ollama_path))

        title = ai.generate_title_from_text(sample_invoice_text)

        # Assertions
        assert title is not None
        assert len(title) > 0
        assert len(title) <= 127
        print(f"Generated title without API key: {title}")

    def test_generate_title_with_api_key(
        self,
        ollama_base_url,
        settings_ollama_path,
        sample_invoice_text,
    ):
        """Test that title generation works with API key (authenticated Ollama).

        Note: This test will work even if Ollama doesn't require authentication,
        as long as Ollama accepts the Authorization header without error.
        """
        # Check if Ollama is available
        available, msg = check_ollama_available(ollama_base_url)
        if not available:
            pytest.skip(msg)

        # Create OllamaTitles with API key
        # Using a test key - real Ollama may or may not validate it
        api_key = "test-api-key-for-integration-test"
        ai = OllamaTitles(ollama_base_url, api_key=api_key, settings_file=str(settings_ollama_path))

        title = ai.generate_title_from_text(sample_invoice_text)

        # Assertions - should work even if Ollama doesn't validate the key
        # (local Ollama typically doesn't require authentication)
        assert title is not None
        assert len(title) > 0
        assert len(title) <= 127
        print(f"Generated title with API key: {title}")

    def test_generate_title_with_empty_api_key(
        self,
        ollama_base_url,
        settings_ollama_path,
        sample_invoice_text,
    ):
        """Test that title generation works with empty API key (treated as no key)."""
        # Check if Ollama is available
        available, msg = check_ollama_available(ollama_base_url)
        if not available:
            pytest.skip(msg)

        # Create OllamaTitles with empty API key
        ai = OllamaTitles(ollama_base_url, api_key="", settings_file=str(settings_ollama_path))

        title = ai.generate_title_from_text(sample_invoice_text)

        # Should work the same as without API key
        assert title is not None
        assert len(title) > 0
        assert len(title) <= 127
        print(f"Generated title with empty API key: {title}")

    def test_paperless_integration_without_api_key(
        self,
        ollama_base_url,
        settings_ollama_path,
        paperless_url,
        paperless_api_key,
        sample_invoice_text,
    ):
        """Test PaperlessAITitles integration without Ollama API key."""
        # Check if Ollama is available
        available, msg = check_ollama_available(ollama_base_url)
        if not available:
            pytest.skip(msg)

        ai_titles = PaperlessAITitles(
            openai_api_key=None,
            ollama_base_url=ollama_base_url,
            ollama_api_key=None,
            paperless_url=paperless_url,
            paperless_api_key=paperless_api_key,
            settings_file=str(settings_ollama_path),
        )

        # Generate title directly (bypassing Paperless API)
        title = ai_titles.ai.generate_title_from_text(sample_invoice_text)

        assert title is not None
        assert len(title) > 0
        assert len(title) <= 127
        print(f"PaperlessAITitles generated title without API key: {title}")

    def test_paperless_integration_with_api_key(
        self,
        ollama_base_url,
        settings_ollama_path,
        paperless_url,
        paperless_api_key,
        sample_invoice_text,
    ):
        """Test PaperlessAITitles integration with Ollama API key."""
        # Check if Ollama is available
        available, msg = check_ollama_available(ollama_base_url)
        if not available:
            pytest.skip(msg)

        api_key = "test-api-key-for-paperless-integration"
        ai_titles = PaperlessAITitles(
            openai_api_key=None,
            ollama_base_url=ollama_base_url,
            ollama_api_key=api_key,
            paperless_url=paperless_url,
            paperless_api_key=paperless_api_key,
            settings_file=str(settings_ollama_path),
        )

        # Generate title directly (bypassing Paperless API)
        title = ai_titles.ai.generate_title_from_text(sample_invoice_text)

        assert title is not None
        assert len(title) > 0
        assert len(title) <= 127
        print(f"PaperlessAITitles generated title with API key: {title}")

