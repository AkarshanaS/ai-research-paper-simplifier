from openai import OpenAI
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def create_vector_store(embeddings):
    return np.array(embeddings)

def search_similar_chunks(index, query, chunks, top_k=5):
    query_embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    ).data[0].embedding

    similarities = cosine_similarity([query_embedding], index)[0]
    top_indices = similarities.argsort()[-top_k:][::-1]

    return [chunks[i] for i in top_indices]