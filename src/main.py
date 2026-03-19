from src.arxiv_fetcher import fetch_arxiv_papers, fetch_paper_by_id
from src.pdf_downloader import download_pdf
from src.text_extractor import extract_text
from src.chunking import chunk_text
from src.embeddings import create_embeddings
def main():
    print("Welcome to the ArXiv Paper Fetcher!")
    print("1. Search for papers")
    print("2. Fetch paper by ID")

    choice = input("Enter your choice (1 or 2): ").strip()
    if choice == '1':
        query = input("Enter your search query: ").strip()
        results = fetch_arxiv_papers(query)

        if not results:
            print("No papers found for your query.")
            return
        print("\nTop Results:\n")
        for i, paper in enumerate(results, start=1):
            print(f"{i}. {paper['title']} by {', '.join(paper['authors'])}")
            print(f"   Published: {paper['published']}")
            print(f"   URL: {paper['url']}\n")

        print("Enter the number of the paper you want to download as a PDF, or '0' to exit.")
        selection = input("Your choice: ").strip()
        if selection == '0':
            print("Exiting.")
            return
        elif selection.isdigit() and 1 <= int(selection) <= len(results):
            selected_paper = results[int(selection) - 1]
            paper_id = selected_paper['url'].split('/')[-1]
            file_path = download_pdf(paper_id)
            if file_path:
                text = extract_text(file_path)
                print("\nFirst 500 words of extracted text:\n")
                print(text[:500])
            else:
                print("Failed to download the PDF.")
            
        else:
            print("Invalid selection. Please enter a valid number.")                        

    elif choice == '2':
        paper_id = input("Enter the ArXiv paper ID (e.g., 2101.00001): ").strip()
        paper = fetch_paper_by_id(paper_id)

        if not paper:
            print("No paper found with the given ID.")
            return
        
        print("\nPaper Details:\n")
        print(f"\nTitle: {paper['title']}")
        print(f"Authors: {', '.join(paper['authors'])}")
        print(f"Published: {paper['published']}")
        print(f"URL: {paper['url']}")
        print(f"Summary: {paper['summary']}")
        print("\nDo you want to download this paper as a PDF? (y/n)")
        download_choice = input("Your choice: ").strip().lower()
        if download_choice == 'y':
            file_path = download_pdf(paper_id)
            if file_path:
                text = extract_text(file_path)
                print("\n Extracted text...\n")
                print("\nFirst 500 words of extracted text:\n")
                print(text[:500])
            else:
                print("Failed to download the PDF.")
            print("Exiting without downloading.")
        else:
            print("Invalid choice. Please enter 1 or 2.")
    
    chunks = chunk_text(text)
    print(f"\nTotal chunks created: {len(chunks)}\n")
    print("First chunk preview:\n")
    print(chunks[0])  

    embeddings = create_embeddings(chunks)
    print(f"\nNumber of embeddings created: {len(embeddings)}")
    print(f"Embedding shape: {len(embeddings[0])}")

if __name__ == "__main__":
    main()
