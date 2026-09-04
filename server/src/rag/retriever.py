from src.rag.embedder import embed_texts
from src.rag.chroma_client import get_knowledge_collection

async def retrieve_context(text:str, limit: int = 4) -> list[dict]:
    if not isinstance(text, str) or text.strip() == "":
        raise ValueError("Text must not be an empty string")

    vectors = await embed_texts([text])
    collection = get_knowledge_collection()
    result = collection.query(
        query_embeddings=vectors,
        n_results=limit
    )
    documents = result["documents"][0] # ["Insomnia disorder text here...", "More related text..."]
    metadatas = result["metadatas"][0] # [{"source_document": "DSM 5 TR-APA (2022).pdf", "page": 340, "chunk_index": 340},{"source_document": "DSM 5 TR-APA (2022).pdf", "page": 341, "chunk_index": 341},]
    distances = result["distances"][0] # [0.12, 0.19]

    retrieved_query: list[dict] = []
    for doc, meta, dis in zip(documents,metadatas,distances):
        if len(doc.strip()) < 100:  # skip short/junk fragments like titles, headers
            continue
        retrieved_query.append({
        "text": doc,
        "source_document": meta["source_document"],
        "page": meta["page"],
        "distance": dis,
    })

    return retrieved_query