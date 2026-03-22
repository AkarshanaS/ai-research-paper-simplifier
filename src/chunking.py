def chunk_text(pages_data, chunk_size=500, overlap=100):
    """
    Splits the input text into chunks of specified size with optional overlap.
    
    Args:
        pages_data (List[Dict]): A list of dictionaries containing text and page labels.
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
    for entry in pages_data:
        text = entry["text"]
        page_num = entry["page_label"]

    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk_content = text[start:end]
        chunks.append({
                "text": chunk_content,
                "page": page_num
            })
        start += chunk_size - overlap
    
    return chunks
