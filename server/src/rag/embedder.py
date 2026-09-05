# server/src/rag/embedder.py

# Import our validated app settings (provider choice, model names, API key)
from src.core.config import settings
# OllamaEmbeddings talks to a locally running Ollama server to generate embeddings
from langchain_ollama import OllamaEmbeddings
# NVIDIAEmbeddings talks to NVIDIA's hosted embedding API as a fallback option
from langchain_huggingface import HuggingFaceEndpointEmbeddings


def check_text(text: str) -> str:
    # Confirm the input is actually a string, not None, a number, or something else
    if isinstance(text, str) and text is not None and text.strip() != "":
        # .strip() removes leading/trailing whitespace so we don't embed blank padding
        return text.strip()
    else:
        # Raise a clear error immediately rather than letting bad data flow further downstream
        raise ValueError("text must be a string")


async def _get_ollama_embeddings(texts: list[str]) -> list[list[float | int]]:
    # Create an Ollama embeddings client pointing at your local Ollama server
    client = OllamaEmbeddings(
        model=settings.OLLAMA_EMBEDDING_MODEL,   # e.g. "nomic-embed-text", from settings
        base_url=settings.OLLAMA_BASE_URL,        # e.g. "http://localhost:11434", from settings
    )
    # embed_documents() sends all texts and returns one vector per text
    return await client.aembed_documents(texts)

async def _get_huggingface_embeddings(texts: list[str]) -> list[list[float | int]]:
    embeddings = HuggingFaceEndpointEmbeddings(
        model="Qwen/Qwen3-Embedding-8B",
        huggingfacehub_api_token=settings.HUGGING_FACE_API_KEY
    )
    return await embeddings.aembed_documents(texts)


#####################################################################################################
#                                   Main Function to execute
# Signature: list of Strings,                                  Return Value: Multi dimension vectors
#####################################################################################################
async def embed_texts(texts: list[str]) -> list[list[float | int]]:
    # Reject an empty list immediately — nothing meaningful to embed
    if not texts:
        raise ValueError("texts must contain at least one non-empty string")

    # Reject anything that isn't actually a list (e.g. someone passing a single string)
    if not isinstance(texts, list):
        raise TypeError("texts must be a list")

    # Build a cleaned list of texts, validating each one along the way
    docs = []
    for text in texts:
        docs.append(check_text(text))  # check_text() strips whitespace and rejects bad input

    # Route to the correct provider based on what's configured in .env
    if settings.EMBEDDING_PROVIDER == "ollama":
        vectors = await _get_ollama_embeddings(docs)   # call your local Ollama server

    elif settings.EMBEDDING_PROVIDER == "huggingface":
        vectors = await _get_huggingface_embeddings(docs)
    else:
        # This should be unreachable now thanks to the config.py validator,
        # but we keep this check as a safety net in case settings are ever bypassed
        raise ValueError("Embedding provider must be one of 'nvidia' or 'ollama'")

    # Sanity check: we should get back exactly one vector per input text
    if len(vectors) != len(docs):
        raise RuntimeError("Embedding provider returned an unexpected number of vectors")

    # Every vector should have the same number of dimensions —
    # grab the first one's length as our expected size to compare against
    expected_dimension = len(vectors[0])

    # Loop through every returned vector to check it's well-formed
    for vector in vectors:
        if not vector:
            # An empty vector means the provider failed silently — catch it here instead of later
            raise RuntimeError("Embedding provider returned an empty vector")

        if len(vector) != expected_dimension:
            # Mixed dimensions would break ChromaDB's similarity math — catch it early
            raise RuntimeError("Embedding provider returned inconsistent vector dimensions")

        if not all(isinstance(value, (int, float)) for value in vector):
            # Every number in the vector must actually be numeric, not a string or None
            raise RuntimeError("Embedding provider returned non-numeric vector values")

    # All checks passed — return the clean list of vectors
    return vectors