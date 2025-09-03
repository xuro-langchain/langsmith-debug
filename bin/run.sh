#!/usr/bin/env bash
set -euo pipefail

# Load .env from project root if present
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
if [ -f "$PROJECT_ROOT/.env" ]; then
 set -a
 . "$PROJECT_ROOT/.env"
 set +a
fi

# Ensure required secrets exist
if [ -z "${OPENAI_API_KEY:-}" ] || [ -z "${WEAVIATE_URL:-}" ] || [ -z "${WEAVIATE_API_KEY:-}" ]; then
 echo "Missing required environment variables: OPENAI_API_KEY, WEAVIATE_URL, WEAVIATE_API_KEY" >&2
 exit 1
fi

GENERATED_CREDS_FILES=$(python3 "$PROJECT_ROOT/creds.py")

docker run -it --rm \
 --name langsmith-debug \
 -p 5678:5678 \
 -e GENERIC_TIMEZONE="America/New York" \
 -e TZ="America/New York" \
 -e N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true \
 -e N8N_RUNNERS_ENABLED=true \
 -e LANGCHAIN_ENDPOINT="${LANGSMITH_ENDPOINT:-https://api.smith.langchain.com}" \
 -e LANGCHAIN_API_KEY="${LANGSMITH_API_KEY}" \
 -e LANGCHAIN_TRACING_V2=true \
 -e LANGCHAIN_PROJECT="${LANGSMITH_PROJECT:-langsmith-debug}" \
 -e DB_SQLITE_POOL_SIZE=1 \
 -e N8N_BLOCK_ENV_ACCESS_IN_NODE=false \
 ${N8N_ENCRYPTION_KEY:+-e N8N_ENCRYPTION_KEY="$N8N_ENCRYPTION_KEY"} \
 -v n8n_data:/home/node/.n8n \
 -v "$PROJECT_ROOT/agents/basic.json":/workflows/basic.json:ro \
 -v "$PROJECT_ROOT/agents/reflective.json":/workflows/reflective.json:ro \
 -v "$PROJECT_ROOT/agents/guardrail_reflective.json":/workflows/guardrail_reflective.json:ro \
 -v "$(echo $GENERATED_CREDS_FILES | awk '{print $1}')":/imports/credentials_openai.json:ro \
 -v "$(echo $GENERATED_CREDS_FILES | awk '{print $2}')":/imports/credentials_weaviate.json:ro \
 --entrypoint /bin/sh \
 n8nio/n8n -c '
 set -e
 # If credentials already exist, skip import to avoid duplicates
 if ! n8n export:credentials --all --output=/tmp/_creds.json >/dev/null 2>&1; then
   echo "Warning: could not list credentials; proceeding to import"
   n8n import:credentials --input=/imports/credentials_openai.json --decrypted || true
   n8n import:credentials --input=/imports/credentials_weaviate.json --decrypted || true
 else
   if ! grep -q "OpenAi Account" /tmp/_creds.json; then
     n8n import:credentials --input=/imports/credentials_openai.json --decrypted || true
   fi
   if ! grep -q "Weaviate Credentials Account" /tmp/_creds.json; then
     n8n import:credentials --input=/imports/credentials_weaviate.json --decrypted || true
   fi
 fi
 n8n import:workflow --input=/workflows/basic.json
 n8n import:workflow --input=/workflows/reflective.json
 n8n import:workflow --input=/workflows/guardrail_reflective.json
 n8n start'


