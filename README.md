## LangSmith Workshop - Debugging Agents

### Prerequisites
- Docker and Docker Desktop installed and running
- Python 3.10+ available as `python3`

### Create your .env
- Copy the example file and fill in the values:
```
cp .env.example .env
```
- You’ll need accounts/keys for:
  - OpenAI (for model and embeddings)
  - Weaviate Cloud (for vector store). Note: free Weaviate Cloud clusters expire after 14 days.
- Open `.env` and provide values for the required variables (see `.env.example`).

### Create and activate a virtual environment
```
python3 -m venv .venv
source .venv/bin/activate
```

### Install dependencies
```
pip install -r requirements.txt
```

### Initialize the Weaviate database
```
bash bin/install.sh
```

### Start n8n and open the UI
```
bash bin/run.sh
```
Then visit `http://localhost:5678` in your browser.


