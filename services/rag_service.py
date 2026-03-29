from src.main import answer_question, summarize_paper

def ask(query, index, chunks, mode):
    return answer_question(query, index, chunks, mode)

def summarize(index, chunks, mode):
    return summarize_paper(index, chunks, mode)