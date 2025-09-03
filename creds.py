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

    if not openai_key or not weaviate_url or not weaviate_key:
        raise SystemExit(
            "Missing environment: OPENAI_API_KEY, WEAVIATE_URL, WEAVIATE_API_KEY"
        )

    credentials = [
        {
            "id": create_random_id(),
            "name": "OpenAi Account",
            "type": "openAiApi",
            "data": {"apiKey": openai_key},
        },
        {
            "id": create_random_id(),
            "name": "Weaviate Credentials Account",
            "type": "weaviateApi",
            "data": {"endpoint": weaviate_url, "apiKey": weaviate_key},
        },
    ]

    project_root = Path(__file__).resolve().parents[1]
    out_path = project_root / "credentials_import.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(credentials, f, ensure_ascii=False, indent=2)

    print(str(out_path))


if __name__ == "__main__":
    main()


