# server/src/rag/ingest.py

from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
from src.rag.embedder import embed_texts
from src.rag.chroma_client import get_knowledge_collection
from src.core.config import settings


# print(Path(__file__).resolve().parents[2] / settings.KNOWLEDGE_DIR)

def process_pdf_pages(pages: list, source_name: str) -> list[dict]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunk_records = []
    global_chunk_index = 0

    for page in pages:
        page_chunks = splitter.split_text(page.page_content)
        for chunk_text in page_chunks:
            chunk_records.append({
                "text": chunk_text,
                "source_document": source_name,
                "page": page.metadata.get("page", None),
                "chunk_index": global_chunk_index,
            })
            global_chunk_index += 1

    return chunk_records

#####################################################################################################
#                                   Main Function to execute
# Signature: Path,                                                              Return Value: None
#####################################################################################################
async def ingest_folder(data_path: str = settings.KNOWLEDGE_DIR) -> None:
    p = Path(__file__).resolve().parents[2] / data_path
    pdf_files = list(p.glob("*.pdf"))

    if not pdf_files:
        raise ValueError(f"No PDF files found in: {p}")

    all_chunk_records = []

    for pdf_path in pdf_files:
        loader = PyPDFLoader(str(pdf_path))
        pages = loader.load()
        file_chunks = process_pdf_pages(pages, source_name=pdf_path.name)
        all_chunk_records.extend(file_chunks)

    if not all_chunk_records:
        raise ValueError(f"No chunks were produced from folder: {p}")

    # Keep batch size well under ChromaDB limit (5461) and within API provider payload limits
    BATCH_SIZE = 500
    for i in range(0, len(all_chunk_records), BATCH_SIZE):
        # Extract that that batch size equivalent records
        batch_records = all_chunk_records[i:i+BATCH_SIZE]
        # Extract the only text part of that batch
        batch_texts = [r["text"] for r in batch_records]
        batch_vectors = await embed_texts(batch_texts)
        # Extract the IDs for that batch
        batch_ids = [
            f"{r['source_document']}_chunk_{r['chunk_index']}"
            for r in batch_records
        ]
        # Extract the metadata for that batch
        batch_metadata = [
            {
                "source_document": r["source_document"],
                "page": r["page"],
                "chunk_index": r["chunk_index"],
                "active_embedding_provider": settings.EMBEDDING_PROVIDER,
            }
            for r in batch_records
        ]
        collection = get_knowledge_collection()
        total_chunks = len(all_chunk_records)
        # Use upsert to allow idempotent re-running of ingestion tests
        collection.upsert(
            documents=batch_texts,
            embeddings=batch_vectors,
            metadatas=batch_metadata,
            ids=batch_ids,
        )
    print(f"Successfully ingested {total_chunks} chunks from {len(pdf_files)} file(s).")