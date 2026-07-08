import os
from dotenv import load_dotenv
 
# Load environment variables
load_dotenv()
 
# Paths
DATA_FOLDER = "data"
RAW_PDFS_FOLDER = os.path.join(DATA_FOLDER, "raw_pdfs")
CSV_FILE = os.path.join(DATA_FOLDER, "card_data.csv")
CHUNKS_FILE = os.path.join(DATA_FOLDER, "chunks.json")
DB_FOLDER = "database"
DB_PATH = os.path.join(DB_FOLDER, "credit_cards.db")
 
# Pinecone settings
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "credit-cards")
 
# OpenAI settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-3-small"
 
# LangSmith settings for tracing
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "InteligentCreditCard")

# Set environment variables for LangSmith (required by LangChain)
if LANGSMITH_TRACING and LANGSMITH_API_KEY:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = LANGSMITH_ENDPOINT
    os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = LANGSMITH_PROJECT
    print(f"✅ LangSmith tracing enabled for project: {LANGSMITH_PROJECT}")
 
# Chunking settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
KEYWORDS = ["reward", "point", "cap", "exclude", "transfer", "eligible", "benefit", "fee", "milestone"]
 
# Create directories if not exist
os.makedirs(DB_FOLDER, exist_ok=True)
os.makedirs(RAW_PDFS_FOLDER, exist_ok=True)