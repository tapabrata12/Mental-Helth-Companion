from src.core.config import settings


async def check_text(text: str)-> str:
    if isinstance(text, str) and text is not None and text.strip() is not "" and text.isdigit() is False:
        return text.strip()
    else:
        raise ValueError("text must be a string")


async def _get_nvidia_embeddings(texts: list[str]):
    pass

async def _get_ollama_embeddings(texts: list[str]):
    pass

#####################################################################################################
#                                   Main Function to execute
# Signature: list of Strings,                                  Return Value: Multi dimension vectors
#####################################################################################################
async def embed_texts(texts: list[str]):
    if not isinstance(texts, list):
        raise TypeError("texts must be a list")

    docs = []
    for text in texts:
        docs.append(await check_text(text))

    if settings.EMBEDDING_PROVIDER == "nvidia":
        pass
    elif settings.EMBEDDING_PROVIDER == "ollama":
        pass
    else:
        raise ValueError("Embedding provider must be one of 'nvidia' or 'ollama'")
