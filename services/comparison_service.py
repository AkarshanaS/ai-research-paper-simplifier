from src.vector_store import search_similar_chunks
from src.llm import generate_answer

def compare_papers(paper1, paper2, mode):
    index1, chunks1 = paper1["index"], paper1["chunks"]
    index2, chunks2 = paper2["index"], paper2["chunks"]

    #getting context for both papers based on key sections
    ctx1 = search_similar_chunks(index1, "main idea method results", chunks1, top_k=8)
    ctx2 = search_similar_chunks(index2, "main idea method results", chunks2, top_k=8)

    text1 = "\n".join([c["text"] for c in ctx1])
    text2 = "\n".join([c["text"] for c in ctx2])

    query = f"""
Compare these two research papers:

Paper 1:
{text1}

Paper 2:
{text2}

Format your response EXACTLY like this:

##  🔑 Key Idea Comparison
- ...

## ⚙️ Methods Comparison
- ...

## ✅ Strengths & Weaknesses
- ...

## 🎯 When to Use Each
- ...
"""

    response = generate_answer(query, [text1, text2], mode)
    return response