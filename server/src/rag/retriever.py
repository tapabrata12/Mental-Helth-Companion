from src.rag.embedder import embed_texts
from src.rag.chroma_client import get_knowledge_collection

async def retrieve_embeddings_from_db(text:str, limit: int = 4) -> list[list[float | int]]:
    if not isinstance(text, str) and text.strip() == "":
        raise ValueError("Text must not be an empty string")

    vectors = embed_texts([text])