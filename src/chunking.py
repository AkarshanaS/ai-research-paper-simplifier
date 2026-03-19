def chunk_text(text, chunk_size=500, overlap=100):
    """
    Splits the input text into chunks of specified size with optional overlap.
    
    Args:
        text (str): The input text to be chunked.
        chunk_size (int): The maximum size of each chunk in characters.
        overlap (int): The number of characters to overlap between chunks.
        
    Returns:
        List[str]: A list of text chunks.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0.")
    if overlap < 0:
        raise ValueError("overlap must be non-negative.")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size.")
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunks.append(text[start:end])
        start += chunk_size - overlap
    
    return chunks
