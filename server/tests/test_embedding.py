import asyncio
from src.rag.embedder import embed_texts

vectors = asyncio.run(embed_texts(["Feeling anxious and unable to sleep."]))
print(len(vectors))        # should print 1 (one text in, one vector out)
print(len(vectors[0]))     # should print the embedding dimension, e.g. 768