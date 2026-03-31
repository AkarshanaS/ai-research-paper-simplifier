from src.vector_store import search_similar_chunks
from src.llm import generate_answer

def compare_papers(paper1, paper2, mode):
    index1, chunks1 = paper1["index"], paper1["chunks"]
    index2, chunks2 = paper2["index"], paper2["chunks"]

    ctx1 = search_similar_chunks(index1, "main idea method results contributions", chunks1, top_k=8)
    ctx2 = search_similar_chunks(index2, "main idea method results contributions", chunks2, top_k=8)

    text1 = "\n".join([c["text"] for c in ctx1])
    text2 = "\n".join([c["text"] for c in ctx2])

    query = f"""Compare these two research papers using EXACTLY this format.
Each section must be separated by a blank line.
Each section starts with the label on its own line (no asterisks, no markdown),
followed by exactly two bullet lines starting with "- Paper 1:" and "- Paper 2:".

Key Idea:
- Paper 1: <one sentence>
- Paper 2: <one sentence>

Methods:
- Paper 1: <one sentence>
- Paper 2: <one sentence>

Strengths:
- Paper 1: <one sentence>
- Paper 2: <one sentence>

Use Cases:
- Paper 1: <one sentence>
- Paper 2: <one sentence>

Paper 1 content:
{text1}

Paper 2 content:
{text2}
"""

    response = generate_answer(query, [text1, text2], mode)
    return response