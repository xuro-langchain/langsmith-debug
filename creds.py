#!/usr/bin/env python3
import json
import os
import random
import string
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(".env")

def create_random_id(length: int = 16) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(random.choice(alphabet) for _ in range(length))


def main() -> None:
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    weaviate_url = os.environ.get("WEAVIATE_URL", "")
    weaviate_key = os.environ.get("WEAVIATE_API_KEY", "")
    tavily_key = os.environ.get("TAVILY_API_KEY", "")

    if not openai_key or not weaviate_url or not weaviate_key or not tavily_key:
        raise SystemExit(
            "Missing environment: OPENAI_API_KEY, WEAVIATE_URL, WEAVIATE_API_KEY, TAVILY_API_KEY"
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

    tavily_payload = [
        {
            "id": create_random_id(),
            "name": "Tavily Account",
            "type": "tavilyApi",
            "data": {"apiKey": tavily_key},
        }
    ]

    openai_out = project_root / "credentials_openai.json"
    weaviate_out = project_root / "credentials_weaviate.json"
    tavily_out = project_root / "credentials_tavily.json"

    with openai_out.open("w", encoding="utf-8") as f:
        json.dump(openai_payload, f, ensure_ascii=False, indent=2)
    with weaviate_out.open("w", encoding="utf-8") as f:
        json.dump(weaviate_payload, f, ensure_ascii=False, indent=2)
    with tavily_out.open("w", encoding="utf-8") as f:
        json.dump(tavily_payload, f, ensure_ascii=False, indent=2)
       
    paths = [str(openai_out), str(weaviate_out), str(tavily_out)]

    # Print generated paths space-separated for easy parsing
    print(" ".join(paths))


if __name__ == "__main__":
    main()


