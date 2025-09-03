#!/usr/bin/env python3
import json
import os
import random
import string
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv(".env")

def create_random_id(length: int = 16) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(random.choice(alphabet) for _ in range(length))


def main() -> None:
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    weaviate_url = os.environ.get("WEAVIATE_URL", "")
    weaviate_key = os.environ.get("WEAVIATE_API_KEY", "")

    if not openai_key or not weaviate_url or not weaviate_key:
        raise SystemExit(
            "Missing environment: OPENAI_API_KEY, WEAVIATE_URL, WEAVIATE_API_KEY"
        )

    # Create two separate files, each with a single-element array
    project_root = Path(__file__).resolve().parents[1]

    openai_payload = [
        {
            "id": create_random_id(),
            "name": "OpenAi Account",
            "type": "openAiApi",
            "data": {"apiKey": openai_key},
        }
    ]
    weaviate_payload = [
        {
            "id": create_random_id(),
            "name": "Weaviate Credentials Account",
            "type": "weaviateApi",
            "data": {
                "weaviate_api_key": weaviate_key,
                "weaviate_cloud_endpoint": weaviate_url,
            },
        }
    ]

    openai_out = project_root / "credentials_openai.json"
    weaviate_out = project_root / "credentials_weaviate.json"

    with openai_out.open("w", encoding="utf-8") as f:
        json.dump(openai_payload, f, ensure_ascii=False, indent=2)
    with weaviate_out.open("w", encoding="utf-8") as f:
        json.dump(weaviate_payload, f, ensure_ascii=False, indent=2)

    # Print both paths space-separated for easy parsing
    print(f"{openai_out} {weaviate_out}")


if __name__ == "__main__":
    main()


