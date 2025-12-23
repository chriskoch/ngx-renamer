"""Client for interacting with Paperless NGX API."""

from typing import Dict, Any
import requests
from modules.logger import get_logger
from modules.exceptions import PaperlessAPIError


class PaperlessClient:
    """Client for Paperless NGX API operations."""

    def __init__(self, base_url: str, api_key: str) -> None:
        """Initialize Paperless client.

        Args:
            base_url: Paperless NGX API base URL
            api_key: Paperless NGX API authentication token
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self._logger = get_logger(self.__class__.__name__)

        self._headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json",
        }

    def get_document(self, document_id: str) -> Dict[str, Any]:
        """Fetch document details from Paperless NGX.

        Args:
            document_id: Document ID to retrieve

        Returns:
            Document details as dictionary

        Raises:
            PaperlessAPIError: If request fails
        """
        url = f"{self.base_url}/documents/{document_id}/"

        try:
            response = requests.get(url, headers=self._headers, timeout=30)

            if response.status_code == 200:
                self._logger.info(f"Successfully retrieved document {document_id}")
                return response.json()
            else:
                error_msg = (
                    f"Failed to get document {document_id}. "
                    f"Status code: {response.status_code}. "
                    f"Response: {response.text}"
                )
                self._logger.error(error_msg)
                raise PaperlessAPIError(error_msg)

        except requests.RequestException as e:
            error_msg = f"Network error fetching document {document_id}: {e}"
            self._logger.error(error_msg)
            raise PaperlessAPIError(error_msg) from e

    def update_document_title(self, document_id: str, new_title: str) -> None:
        """Update document title in Paperless NGX.

        Args:
            document_id: Document ID to update
            new_title: New title to set

        Raises:
            PaperlessAPIError: If update fails
        """
        url = f"{self.base_url}/documents/{document_id}/"
        payload = {"title": new_title}

        try:
            response = requests.patch(
                url,
                json=payload,
                headers=self._headers,
                timeout=30
            )

            if response.status_code == 200:
                self._logger.info(
                    f"Successfully updated document {document_id} "
                    f"title to: {new_title}"
                )
            else:
                error_msg = (
                    f"Failed to update document {document_id}. "
                    f"Status code: {response.status_code}. "
                    f"Response: {response.text}"
                )
                self._logger.error(error_msg)
                raise PaperlessAPIError(error_msg)

        except requests.RequestException as e:
            error_msg = f"Network error updating document {document_id}: {e}"
            self._logger.error(error_msg)
            raise PaperlessAPIError(error_msg) from e
