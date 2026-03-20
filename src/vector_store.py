import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def create_vector_store(embeddings):
    return np.array(embeddings)

def search_similar_chunks(index, query, model, chunks, top_k=3):
    query_embedding = model.encode([query])
    
    similarities = cosine_similarity(query_embedding, index)[0]
    
    top_indices = similarities.argsort()[-top_k:][::-1]
    
    return [chunks[i] for i in top_indices]