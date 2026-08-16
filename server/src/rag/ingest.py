# server/src/rag/ingest.py

from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
from src.rag.embedder import embed_texts
from src.rag.chroma_client import get_knowledge_collection
from src.core.config import settings


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

    # Extract just the text for batch embedding
    texts = [record["text"] for record in all_chunk_records]

    # One batch call — not looped
    vectors = await embed_texts(texts)

    # Predictable IDs, safe for re-ingestion (upsert instead of duplicate)
    ids = [
        f"{record['source_document']}_chunk_{record['chunk_index']}"
        for record in all_chunk_records
    ]

    # Metadata only — text itself goes in `documents`, not here
    metadata = [{
                "source_document": record["source_document"],
                "page": record["page"],
                "chunk_index": record["chunk_index"],
                "active_embedding_provider": settings.EMBEDDING_PROVIDER
        } for record in all_chunk_records
    ]

    collection = get_knowledge_collection()

    collection.add(
        documents=texts,
        embeddings=vectors,
        metadatas=metadata,
        ids=ids,
    )

    print(f"Ingested {len(texts)} chunks from {len(pdf_files)} file(s).")