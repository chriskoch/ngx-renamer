#!/usr/bin/env python3
"""
Paperless NGX AI Title Generator - Standalone Single-File Version
==================================================================

This is a simplified, all-in-one version of ngx-renamer that requires no
virtual environment setup. All configuration is done via environment variables.

Prerequisites:
- Paperless NGX container must have 'openai' and 'requests' packages installed
  (usually already present in the Paperless NGX image)

Configuration via Environment Variables:
- DOCUMENT_ID: Provided automatically by Paperless NGX
- OPENAI_API_KEY: Your OpenAI API key
- PAPERLESS_NGX_URL: URL to Paperless instance (e.g., http://webserver:8000)
- PAPERLESS_NGX_API_KEY: Your Paperless API token
- OPENAI_MODEL: (Optional) Model to use, default: gpt-4o-mini
- TITLE_WITH_DATE: (Optional) Include date prefix in title, default: false
- TITLE_FORMAT: (Optional) Custom title format instruction

Docker-compose usage:
  webserver:
    volumes:
      - ./ngx-renamer-standalone.py:/usr/local/bin/ngx-renamer.py:ro
    environment:
      PAPERLESS_POST_CONSUME_SCRIPT: python3 /usr/local/bin/ngx-renamer.py
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      PAPERLESS_NGX_URL: http://webserver:8000
      PAPERLESS_NGX_API_KEY: ${PAPERLESS_API_KEY}
      OPENAI_MODEL: gpt-4o
"""

import os
import sys
from datetime import datetime

# Dependency check
try:
    from openai import OpenAI
    import requests
except ImportError as e:
    print(f"ERROR: Required package not found: {e}")
    print("This script requires 'openai' and 'requests' packages.")
    print("These are usually pre-installed in Paperless NGX containers.")
    sys.exit(1)


# Configuration from environment variables
DOCUMENT_ID = os.environ.get('DOCUMENT_ID')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
PAPERLESS_URL = os.environ.get('PAPERLESS_NGX_URL', 'http://localhost:8000')
PAPERLESS_API_KEY = os.environ.get('PAPERLESS_NGX_API_KEY')
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')
TITLE_WITH_DATE = os.environ.get('TITLE_WITH_DATE', 'false').lower() in ('true', '1', 'yes')

# Default prompt for title generation
DEFAULT_PROMPT = """You are a document title generator for a document management system. Generate a concise, descriptive title for the OCR-extracted text below.

Requirements:
- Title length: 50-100 characters (max 127)
- Language: Use the same language as the document
- Format: "Sender - Brief Description" (e.g., "Amazon - Monthly Subscription Invoice")
- Include sender/author only if clearly identifiable in the text
- Focus on document purpose and content, not formatting artifacts
- Do NOT include dates, timestamps, or date references in the title
- Avoid OCR noise, headers, footers, and page numbers

Output only the title text, nothing else.

Document text:
"""

DATE_SUFFIX_PROMPT = """

IMPORTANT: Extract the document date and prefix the title with it in YYYY-MM-DD format.
If no date is found, use {current_date}.
Format: "YYYY-MM-DD Sender - Description"
"""


def get_document_details(document_id):
    """Fetch document details from Paperless NGX API."""
    headers = {
        "Authorization": f"Token {PAPERLESS_API_KEY}",
        "Content-Type": "application/json",
    }

    url = f"{PAPERLESS_URL}/documents/{document_id}/"

    try:
        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get document details. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"Error fetching document details: {e}")
        return None


def update_document_title(document_id, new_title):
    """Update document title in Paperless NGX."""
    headers = {
        "Authorization": f"Token {PAPERLESS_API_KEY}",
        "Content-Type": "application/json",
    }

    url = f"{PAPERLESS_URL}/documents/{document_id}/"
    payload = {"title": new_title}

    try:
        response = requests.patch(url, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            print(f"✓ Title successfully updated to: {new_title}")
            return True
        else:
            print(f"Failed to update title. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error updating document title: {e}")
        return False


def generate_title(content):
    """Generate title using OpenAI API."""
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)

        # Build prompt
        prompt = os.environ.get('TITLE_PROMPT', DEFAULT_PROMPT)

        if TITLE_WITH_DATE:
            current_date = datetime.today().strftime("%Y-%m-%d")
            date_prompt = DATE_SUFFIX_PROMPT.replace("{current_date}", current_date)
            prompt += date_prompt

        # Add document content
        prompt += "\n\n" + content

        # Call OpenAI API
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
        )

        title = response.choices[0].message.content.strip()

        # Ensure title doesn't exceed max length
        if len(title) > 127:
            title = title[:124] + "..."

        return title

    except Exception as e:
        print(f"Error generating title with OpenAI: {e}")
        return None


def main():
    """Main entry point for the script."""
    print("[ngx-renamer-standalone] Starting title generation...")

    # Validate configuration
    if not DOCUMENT_ID:
        print("ERROR: DOCUMENT_ID environment variable not provided")
        sys.exit(1)

    if not OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY environment variable not set")
        sys.exit(1)

    if not PAPERLESS_API_KEY:
        print("ERROR: PAPERLESS_NGX_API_KEY environment variable not set")
        sys.exit(1)

    print(f"Document ID: {DOCUMENT_ID}")
    print(f"Paperless URL: {PAPERLESS_URL}")
    print(f"OpenAI Model: {OPENAI_MODEL}")
    print(f"Include Date: {TITLE_WITH_DATE}")

    # Fetch document details
    print("\nFetching document details from Paperless NGX...")
    document = get_document_details(DOCUMENT_ID)

    if not document:
        print("ERROR: Failed to retrieve document details")
        sys.exit(1)

    print(f"Current title: {document['title']}")

    # Get document content
    content = document.get("content", "")
    if not content:
        print("WARNING: Document has no content (OCR may not have run yet)")
        sys.exit(0)

    # Generate new title
    print("\nGenerating title with OpenAI...")
    new_title = generate_title(content)

    if not new_title:
        print("ERROR: Failed to generate title")
        sys.exit(1)

    print(f"Generated title: {new_title}")

    # Update document
    print("\nUpdating document in Paperless NGX...")
    success = update_document_title(DOCUMENT_ID, new_title)

    if success:
        print("[ngx-renamer-standalone] Completed successfully!")
        sys.exit(0)
    else:
        print("[ngx-renamer-standalone] Failed to update document")
        sys.exit(1)


if __name__ == "__main__":
    main()
