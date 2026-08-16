# server/tests/test_retriever.py

# pytest itself, so we can use pytest.raises and pytest.mark
import pytest
# The function we're actually testing
from src.rag.retriever import retrieve_context
# We need to patch (replace) these two dependencies with fakes
import src.rag.retriever as retriever_module


# A fake version of embed_texts — returns a made-up vector instantly,
# no real network call, no real Ollama server needed
async def fake_embed_texts(texts):
    return [[0.1, 0.2, 0.3]]  # one fake vector, matching the one input text


# A fake ChromaDB collection — returns a hardcoded, predictable result
# shaped exactly like a real collection.query() response
class FakeCollection:
    def query(self, query_embeddings, n_results):
        return {
            "documents": [["Fake insomnia criteria text."]],
            "metadatas": [[{"source_document": "fake.pdf", "page": 42, "chunk_index": 0}]],
            "distances": [[0.15]],
        }


def fake_get_knowledge_collection():
    return FakeCollection()


@pytest.mark.asyncio  # tells pytest this test function is async and needs the asyncio plugin
async def test_retrieve_context_returns_clean_results(monkeypatch):
    # monkeypatch temporarily swaps out the real functions with our fakes,
    # ONLY for the duration of this test — everything reverts afterward automatically
    monkeypatch.setattr(retriever_module, "embed_texts", fake_embed_texts)
    monkeypatch.setattr(retriever_module, "get_knowledge_collection", fake_get_knowledge_collection)

    results = await retrieve_context("what is insomnia disorder")

    # Real assertions — pytest checks these automatically, no human eyeballing needed
    assert len(results) == 1
    assert results[0]["text"] == "Fake insomnia criteria text."
    assert results[0]["source_document"] == "fake.pdf"
    assert results[0]["page"] == 42
    assert results[0]["distance"] == 0.15


@pytest.mark.asyncio
async def test_retrieve_context_rejects_blank_query():
    # pytest.raises checks that calling this actually throws the expected error
    with pytest.raises(ValueError):
        await retrieve_context("")


@pytest.mark.asyncio
async def test_retrieve_context_rejects_whitespace_only_query():
    with pytest.raises(ValueError):
        await retrieve_context("   ")
