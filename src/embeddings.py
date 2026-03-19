def create_embeddings(chunks, model):
    """Create embeddings for the documents.
    
    Args:
        chunks (List[str]): A list of text chunks for which to create embeddings.
    
    Returns:
        dict: A dictionary containing the document names as keys and their corresponding embeddings as values.
    """
    
    embeddings = model.encode(chunks,)
    return embeddings
