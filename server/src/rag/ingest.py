from pathlib import Path
from src.core.config import settings
from langchain_community.document_loaders import PyPDFLoader
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
from src.rag.embedder import embed_texts
from src.rag.chroma_client import get_knowledge_collection
import asyncio

def process_pdf_pages(pages: list, source_name: str) -> list[dict]:
    """
    Takes the list of page Documents from PyPDFLoader, chunks each page's
    text, and returns a list of dictionaries — one per chunk — with
    text + metadata attached.
    """
    pass


async def ingest_folder(data_path: str ) -> None:
    """
       Reads every PDF in the given folder, chunks it, embeds the chunks,
       and saves everything into ChromaDB.
    """
    p = Path(__file__).resolve().parents[2] / data_path
    # print(p)
    # print(p.resolve())  # shows the FULL absolute path Python is looking at
    # print(p.exists())  # True or False?
    # print(list(p.glob("*.pdf")))
    PDF_FILES_OBJECT = p.glob("*.pdf")

    file_list: list = []

    for PDF in PDF_FILES_OBJECT:
        file_list.append(str(p.joinpath(PDF)))

    print(file_list)

    loader = PyPDFLoader(file_list[0])
    pages = await loader.aload()


asyncio.run(ingest_folder(settings.KNOWLEDGE_DIR))