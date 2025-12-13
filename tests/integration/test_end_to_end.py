"""
End-to-end smoke tests for critical paths.

These are the "quick wins" - essential smoke tests that verify
the system works end-to-end.

Run with: pytest -m smoke
"""

import pytest
import responses
from modules.paperless_ai_titles import PaperlessAITitles
from modules.openai_titles import OpenAITitles


@pytest.mark.integration
@pytest.mark.smoke
@pytest.mark.openai
class TestCriticalPaths:
    """Smoke tests for critical functionality."""

    def test_smoke_openai_title_generation(
        self, openai_api_key, settings_valid_path, sample_invoice_text
    ):
        """SMOKE TEST: OpenAI can generate a title."""
        ai = OpenAITitles(openai_api_key, str(settings_valid_path))
        title = ai.generate_title_from_text(sample_invoice_text)

        assert title is not None
        assert len(title) > 0
        assert len(title) <= 127  # Max title length
        print(f"✓ Smoke test passed: Generated title = '{title}'")

    def test_smoke_full_paperless_workflow(
        self,
        openai_api_key,
        paperless_url,
        paperless_api_key,
        settings_valid_path,
        sample_invoice_text,
    ):
        """SMOKE TEST: Full workflow works end-to-end."""

        with responses.RequestsMock() as rsps:
            # Mock Paperless API
            rsps.add(
                responses.GET,
                f"{paperless_url}/documents/1/",
                json={"id": 1, "content": sample_invoice_text, "title": "Old"},
                status=200,
            )
            rsps.add(
                responses.PATCH,
                f"{paperless_url}/documents/1/",
                json={"id": 1, "title": "New Title"},
                status=200,
            )

            # Execute
            ai = PaperlessAITitles(
                openai_api_key,
                paperless_url,
                paperless_api_key,
                str(settings_valid_path),
            )
            ai.generate_and_update_title(1)

            # Verify workflow completed
            assert len(rsps.calls) == 2
            assert rsps.calls[0].request.method == "GET"
            assert rsps.calls[1].request.method == "PATCH"
            print("✓ Smoke test passed: Full workflow")

    def test_smoke_settings_loading(self, openai_api_key, settings_valid_path):
        """SMOKE TEST: Settings load correctly."""
        ai = OpenAITitles(openai_api_key, str(settings_valid_path))

        assert ai.settings is not None
        assert ai.settings.get("openai_model") == "gpt-4o-mini"
        assert ai.settings.get("with_date") is False
        assert "prompt" in ai.settings
        print("✓ Smoke test passed: Settings loaded")
