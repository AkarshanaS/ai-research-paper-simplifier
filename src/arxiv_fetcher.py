import arxiv
client = arxiv.Client()

def fetch_arxiv_papers(query, max_results=5):
    """
    Fetches papers from ArXiv based on a search query.

    Args:
        query (str): The search query to find relevant papers.
        max_results (int): The maximum number of papers to fetch.
        
    Returns:
        List[Dict]: A list of dictionaries containing paper information (title, authors, summary, published date, and URL).
    
    """
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    results = []
    for result in client.results(search):
        paper_info = {
            'title': result.title,
            'authors': [author.name for author in result.authors],
            'summary': result.summary,
            'published': result.published,
            'url': result.entry_id
        }
        results.append(paper_info)
    return results

def fetch_paper_by_id(paper_id):
    search = arxiv.Search(
        query=f"id:{paper_id}",
        max_results=1,
        sort_by=arxiv.SortCriterion.Relevance
    )
    
    for result in client.results(search):
        paper_info = {
            'title': result.title,
            'authors': [author.name for author in result.authors],
            'summary': result.summary,
            'published': result.published,
            'url': result.entry_id
        }
        return paper_info
    return None
