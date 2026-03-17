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
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text 

