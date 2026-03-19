import faiss
import numpy as np
def create_vector_store(embeddings):
    """
    Create a FAISS vector store from the given embeddings.

    Args:
        embeddings (list of list of float): A list of embedding vectors.

    Returns: 
        faiss.IndexFlatL2: A FAISS index containing the embeddings.
    """
    embeddings = np.array(embeddings).astype('float32')
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index

def search_similar_chunks(index, query, model, chunks, top_k=3):
    """
    Search for similar chunks in the FAISS index based on a query.

    Args:
        index (faiss.IndexFlatL2): The FAISS index containing the embeddings.
        query (str): The search query.
        model: The embedding model to convert the query into an embedding vector.
        top_k (int): The number of top similar chunks to return.

    Returns:
        list of int: Indices of the top_k most similar chunks in the index.
    """
    query_embedding = model.encode([query]).astype('float32')
    query_embedding = np.array(query_embedding).reshape(1, -1)
    distances, indices = index.search(query_embedding, top_k)
    results = []
    for i in indices[0]:
        results.append(chunks[i])
    return results