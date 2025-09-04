import os
import weaviate
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import OpenAIEmbeddings
from weaviate.classes.init import Auth
import weaviate.classes as wvc

load_dotenv()

# Set OpenAI API key for Weaviate vectorization
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    os.environ["OPENAI_API_KEY"] = openai_api_key

LANGGRAPH_DOCS = [
    "https://langchain-ai.github.io/langgraph/",
    "https://langchain-ai.github.io/langgraph/tutorials/customer-support/customer-support/",
    "https://langchain-ai.github.io/langgraph/tutorials/chatbots/information-gather-prompting/",
    "https://langchain-ai.github.io/langgraph/tutorials/code_assistant/langgraph_code_assistant/",
    "https://langchain-ai.github.io/langgraph/tutorials/multi_agent/multi-agent-collaboration/",
    "https://langchain-ai.github.io/langgraph/tutorials/multi_agent/agent_supervisor/",
    "https://langchain-ai.github.io/langgraph/tutorials/multi_agent/hierarchical_agent_teams/",
    "https://langchain-ai.github.io/langgraph/tutorials/plan-and-execute/plan-and-execute/",
    "https://langchain-ai.github.io/langgraph/tutorials/rewoo/rewoo/",
    "https://langchain-ai.github.io/langgraph/tutorials/llm-compiler/LLMCompiler/",
    "https://langchain-ai.github.io/langgraph/concepts/high_level/",
    "https://langchain-ai.github.io/langgraph/concepts/low_level/",
    "https://langchain-ai.github.io/langgraph/concepts/agentic_concepts/",
    "https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/",
    "https://langchain-ai.github.io/langgraph/concepts/multi_agent/",
    "https://langchain-ai.github.io/langgraph/concepts/persistence/",
    "https://langchain-ai.github.io/langgraph/concepts/streaming/",
    "https://langchain-ai.github.io/langgraph/concepts/faq/"
]

def get_weaviate_client():
    """Get Weaviate client with authentication"""
    weaviate_url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
    weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
    
    print(f"Attempting to connect to Weaviate at: {weaviate_url}")
    
    try:
        if weaviate_api_key and ".cloud" in weaviate_url:
            # Use Weaviate Cloud Services connection
            print("Connecting to Weaviate Cloud Services...")
            auth_config = Auth.api_key(weaviate_api_key)
            
            # Add OpenAI API key to headers for vectorization
            headers = {}
            if openai_api_key:
                headers["X-Openai-Api-Key"] = openai_api_key
            
            client = weaviate.connect_to_weaviate_cloud(
                cluster_url=weaviate_url,
                auth_credentials=auth_config,
                headers=headers
            )
        else:
            # For local instance without authentication
            print("Connecting to local Weaviate instance...")
            client = weaviate.connect_to_local()
        
        print("Successfully connected to Weaviate!")
        return client
        
    except Exception as e:
        print(f"Failed to connect to Weaviate: {e}")
        print("\nTo fix this issue:")
        print("1. Make sure Weaviate is running locally on port 8080, or")
        print("2. Set the WEAVIATE_URL environment variable to point to your Weaviate instance")
        print("3. If using Weaviate Cloud Services, set WEAVIATE_API_KEY environment variable")
        print("\nExample .env file:")
        print("WEAVIATE_URL=http://localhost:8080")
        print("WEAVIATE_API_KEY=your-api-key-here")
        raise

def create_collection_schema(client):
    """Create the LangGraph docs collection schema"""
    collection_name = "LangGraphDocs"
    
    try:
        # Delete existing collection if it exists
        if client.collections.exists(collection_name):
            client.collections.delete(collection_name)
            print(f"Deleted existing collection: {collection_name}")
    except Exception as e:
        print(f"Note: {e}")
    
    # Create new collection
    collection = client.collections.create(
        name=collection_name,
        vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_openai(
            model="text-embedding-3-small"
        ),
        generative_config=wvc.config.Configure.Generative.openai(),
        properties=[
            wvc.config.Property(
                name="content",
                data_type=wvc.config.DataType.TEXT,
                description="The document content"
            ),
            wvc.config.Property(
                name="source",
                data_type=wvc.config.DataType.TEXT,
                description="The source URL of the document"
            ),
            wvc.config.Property(
                name="title",
                data_type=wvc.config.DataType.TEXT,
                description="The title of the document"
            )
        ]
    )
    
    print(f"Created collection: {collection_name}")
    return collection

def load_and_upload_docs():
    """Load documents from URLs and upload to Weaviate"""
    print("Loading documents from URLs...")
    docs = [WebBaseLoader(url).load() for url in LANGGRAPH_DOCS]
    docs_list = [item for sublist in docs for item in sublist]
    
    print(f"Loaded {len(docs_list)} documents")
    
    # Split documents
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=200, chunk_overlap=0
    )
    doc_splits = text_splitter.split_documents(docs_list)
    
    print(f"Split into {len(doc_splits)} chunks")
    
    # Connect to Weaviate
    client = get_weaviate_client()
    
    try:
        # Create collection
        collection = create_collection_schema(client)
        
        # Prepare data for batch upload
        data_objects = []
        for i, doc in enumerate(doc_splits):
            data_objects.append({
                "content": doc.page_content,
                "source": doc.metadata.get("source", ""),
                "title": doc.metadata.get("title", f"Document {i}")
            })
        
        # Batch upload
        print("Uploading documents to Weaviate...")
        with collection.batch.dynamic() as batch:
            for obj in data_objects:
                batch.add_object(
                    properties=obj
                )
        
        print(f"Successfully uploaded {len(data_objects)} document chunks to Weaviate")
        
        # Verify upload
        response = collection.aggregate.over_all(
            total_count=True
        )
        print(f"Total objects in collection: {response.total_count}")
        
    finally:
        client.close()

def query_weaviate(query_text, limit=5):
    """Query the Weaviate collection"""
    client = get_weaviate_client()
    
    try:
        collection = client.collections.get("LangGraphDocs")
        
        response = collection.query.near_text(
            query=query_text,
            limit=limit,
            return_metadata=wvc.query.MetadataQuery(score=True)
        )
        
        print(f"Query: {query_text}")
        print(f"Found {len(response.objects)} results:")
        
        for i, obj in enumerate(response.objects):
            print(f"\n{i+1}. Score: {obj.metadata.score:.4f}")
            print(f"Source: {obj.properties['source']}")
            print(f"Content: {obj.properties['content'][:200]}...")
            
    finally:
        client.close()

if __name__ == "__main__":
    # Load and upload documents
    load_and_upload_docs()
    
    # Example query
    query_weaviate("How do I create a multi-agent system?")