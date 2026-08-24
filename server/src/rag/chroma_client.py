from pathlib import Path
from src.core.config import settings
import chromadb
from chromadb.config import Settings
CHROMA_DIR = Path(__file__).resolve().parents[2] / settings.CHROMA_DIR
# print(CHROMA_DIR)
COLLECTION_NAME = settings.CHROMA_COLLECTION_NAME

_client = None
_collection = None

def get_chroma_client():
    global _client
    """
    This method for creating / opening the connection
    Step 1: get / create the dir
    Step 2: opens the ChromaDB database at the folder dir path we defined
    :return: chromadb.PersistentClient
    """
    if _client is None:

        CHROMA_DIR.mkdir(exist_ok=True, parents=True)
        _client = chromadb.PersistentClient(path=str(CHROMA_DIR), settings=Settings(anonymized_telemetry=False))
        return _client

    return _client

def get_knowledge_collection():
    global _collection
    """
    Step 1: Open the connection
    Step 2: Create / get the knowledge collection
    """
    if _collection is None:

        client = get_chroma_client()
        _collection = client.get_or_create_collection(name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"})    # use cosine similarity for comparing text meaning
        return _collection

    return _collection