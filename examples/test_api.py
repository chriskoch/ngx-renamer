#!/usr/bin/env python3

import os
import argparse
import requests

from dotenv import load_dotenv

load_dotenv()

paperless_url = os.getenv("PAPERLESS_NGX_URL")
paperless_api_key = os.getenv("PAPERLESS_NGX_API_KEY")


def main():
    parser = argparse.ArgumentParser(description="get some data document")
    parser.add_argument("document_id", type=int)
    args = parser.parse_args()

    document_id = args.document_id
    print(f"Document ID: {document_id}")
    print(f"Paperless URL: {paperless_url}")
    print(f"Paperless API Key: {paperless_api_key}")

    headers = {
        "Authorization": f"Token {paperless_api_key}",
        "Content-Type": "application/json",
    }
    try:
        response = requests.get(
            f"{paperless_url}/documents/{document_id}/", headers=headers
        )
    except Exception as e:
        print(f"Error getting document details: {e}")

    print(f"Response Status Code: {response.status_code}") 

    if response.status_code == 200:
        print(response.json())
    else:
        print(
            f"Failed to get document details from paperless-ngx. Status code: {response.status_code}"
        )
        print(response.text)


if __name__ == "__main__":
    main()