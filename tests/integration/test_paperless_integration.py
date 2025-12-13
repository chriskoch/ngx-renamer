"""
Integration tests for Paperless workflow with mocked API.

These tests:
- Mock Paperless API responses (no Docker needed)
- Make REAL OpenAI API calls
- Test full workflow: fetch → generate → update

Run with: pytest tests/integration/test_paperless_integration.py
"""

import pytest
import responses
from modules.paperless_ai_titles import PaperlessAITitles


@pytest.mark.integration
@pytest.mark.openai
class TestPaperlessWorkflow:
    """Test full Paperless workflow with mocked HTTP."""

    def test_successful_title_generation_and_update(
        self,
        openai_api_key,
        paperless_url,
        paperless_api_key,
        settings_valid_path,
        sample_invoice_text,
    ):
        """Test complete workflow: fetch doc → generate title → update."""

        # Setup mocked Paperless API
        with responses.RequestsMock() as rsps:
            document_id = 123

            # Mock GET /documents/123/
            rsps.add(
                responses.GET,
                f"{paperless_url}/documents/{document_id}/",
                json={
                    "id": document_id,
                    "title": "Untitled Document",
                    "content": sample_invoice_text,
                    "created": "2024-01-15T10:30:00Z",
                },
                status=200,
            )

            # Mock PATCH /documents/123/
            rsps.add(
                responses.PATCH,
                f"{paperless_url}/documents/{document_id}/",
                json={
                    "id": document_id,
                    "title": "Amazon - AWS Monthly Invoice",  # Will be different
                    "content": sample_invoice_text,
                },
                status=200,
            )

            # Execute workflow
            ai = PaperlessAITitles(
                openai_api_key,
                paperless_url,
                paperless_api_key,
                str(settings_valid_path),
            )

            ai.generate_and_update_title(document_id)

            # Verify API was called
            assert len(rsps.calls) == 2
            assert rsps.calls[0].request.method == "GET"
            assert rsps.calls[1].request.method == "PATCH"

            # Verify PATCH payload contains title
            patch_body = rsps.calls[1].request.body
            assert b"title" in patch_body

    def test_document_not_found(
        self,
        openai_api_key,
        paperless_url,
        paperless_api_key,
        settings_valid_path,
    ):
        """Test handling of 404 from Paperless API."""

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{paperless_url}/documents/999/",
                json={"detail": "Not found."},
                status=404,
            )

            ai = PaperlessAITitles(
                openai_api_key,
                paperless_url,
                paperless_api_key,
                str(settings_valid_path),
            )

            # Should handle gracefully (prints error, doesn't crash)
            ai.generate_and_update_title(999)

            # Only GET called, no PATCH
            assert len(rsps.calls) == 1

    def test_paperless_api_error(
        self,
        openai_api_key,
        paperless_url,
        paperless_api_key,
        settings_valid_path,
        sample_invoice_text,
    ):
        """Test handling of 500 error from Paperless API."""

        with responses.RequestsMock() as rsps:
            document_id = 123

            # Mock successful GET
            rsps.add(
                responses.GET,
                f"{paperless_url}/documents/{document_id}/",
                json={
                    "id": document_id,
                    "title": "Original Title",
                    "content": sample_invoice_text,
                },
                status=200,
            )

            # Mock failed PATCH
            rsps.add(
                responses.PATCH,
                f"{paperless_url}/documents/{document_id}/",
                json={"error": "Internal server error"},
                status=500,
            )

            ai = PaperlessAITitles(
                openai_api_key,
                paperless_url,
                paperless_api_key,
                str(settings_valid_path),
            )

            # Should handle gracefully
            ai.generate_and_update_title(document_id)

            # Both calls made, but PATCH failed
            assert len(rsps.calls) == 2


@pytest.mark.integration
class TestPaperlessAPIMocking:
    """Test Paperless API without OpenAI (faster tests)."""

    def test_get_document_details(
        self, paperless_url, paperless_api_key, mock_paperless_document_response
    ):
        """Test fetching document details."""

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{paperless_url}/documents/123/",
                json=mock_paperless_document_response,
                status=200,
            )

            # Test using requests directly
            import requests

            headers = {
                "Authorization": f"Token {paperless_api_key}",
                "Content-Type": "application/json",
            }

            response = requests.get(
                f"{paperless_url}/documents/123/",
                headers=headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == 123
            assert "content" in data
