#!/usr/bin/env python3

import os
import argparse

from dotenv import load_dotenv
import pdfplumber

from modules.openai_titles import OpenAITitles


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

ai = OpenAITitles(api_key, "/usr/src/ngx-renamer/settings.yaml")

def main():
    parser = argparse.ArgumentParser(description="get the title of a pdf document")
    parser.add_argument("filename", type=str)
    args = parser.parse_args()

    with pdfplumber.open(args.filename) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()

    
    new_title = ai.generate_title_from_text(text)
    
    if new_title:
        print(f"Generated Document Title: {new_title}")
    else:
        print("Failed to generate the document title.")

if __name__ == "__main__":
    main()