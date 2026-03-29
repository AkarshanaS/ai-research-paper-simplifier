from src.pdf_downloader import download_pdf
from src.text_extractor import extract_text
from src.main import process_paper

def load_paper(paper_id):
    file_path = download_pdf(paper_id)
    pages = extract_text(file_path)
    index, chunks = process_paper(pages)
    return index, chunks