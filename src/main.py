from src.arxiv_fetcher import fetch_arxiv_papers, fetch_paper_by_id
from src.pdf_downloader import download_pdf
from src.text_extractor import extract_text
from src.chunking import chunk_text
from src.embeddings import create_embeddings
from sentence_transformers import SentenceTransformer
from src.vector_store import create_vector_store, search_similar_chunks
from src.llm import generate_answer
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
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = create_embeddings(chunks, model)
    
    index = create_vector_store(embeddings)
    
    while True:
        query = input('\n\nAsk a question about the paper(Or type "exit" to quit): ')
        if query.lower() == 'exit':
            break

        context_chunks = search_similar_chunks(index, query, model, chunks)
        print('\n Retrieved context:\n')
        for c in context_chunks:
            print(c[:300])
            print('-' * 50)

        #LLM answer generation
        answer = generate_answer(query, context_chunks)
        print("\nAnswer:\n")
        print(answer)

def process_paper(text):
    chunks = chunk_text(text)
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = create_embeddings(chunks, model)
    index = create_vector_store(embeddings)
    return index, model, chunks

def answer_question(query, index, model, chunks):
    context_chunks = search_similar_chunks(index, query, model, chunks)
    answer = generate_answer(query, context_chunks)
    return answer, context_chunks
    
if __name__ == "__main__":
    main()
