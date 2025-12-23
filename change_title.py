#!/usr/bin/env python3

import os

from dotenv import load_dotenv
from modules.paperless_ai_titles import PaperlessAITitles
from modules.logger import get_logger


def main():
    logger = get_logger(__name__)

    document_id=os.environ.get('DOCUMENT_ID')
    run_dir=os.environ.get('RUN_DIR')

    # Try to load .env file if it exists (backward compatibility)
    # If .env doesn't exist, environment variables from docker-compose will be used
    env_file_path = f"{run_dir}/.env" if run_dir else ".env"
    if os.path.exists(env_file_path):
        load_dotenv(env_file_path)
    else:
        # .env file not found, will use environment variables directly
        load_dotenv()  # This will still check current directory

    paperless_url = os.getenv("PAPERLESS_NGX_URL")
    paperless_api_key = os.getenv("PAPERLESS_NGX_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    ollama_base_url = os.getenv("OLLAMA_BASE_URL")
    ollama_api_key = os.getenv("OLLAMA_API_KEY")

    logger.info("Starting Paperless AI Titles")
    logger.info(f"Paperless Document ID: {document_id}")
    logger.info(f"Directory where script runs in container: {run_dir}")

    # PaperlessAITitles will determine provider from settings.yaml
    ai = PaperlessAITitles(
        openai_api_key,
        ollama_base_url,
        ollama_api_key,
        paperless_url,
        paperless_api_key,
        f"{run_dir}/settings.yaml"
    )
    ai.generate_and_update_title(document_id)


if __name__ == "__main__":
    main()
