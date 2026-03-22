import fitz

def extract_text(file_path):
    """
    Extract text from a file.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The extracted text.
    """
    doc = fitz.open(file_path)
    pages_data = []
    for i, page in enumerate(doc):
        pages_data.append({
            "text": page.get_text(),
            "page_label": i + 1
        })
    return pages_data
