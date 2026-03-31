import streamlit as st
from src.arxiv_fetcher import fetch_arxiv_papers
from src.pdf_downloader import download_pdf
from src.text_extractor import extract_text
from src.main import process_paper, answer_question, summarize_paper
from services.paper_service import load_paper
from services.comparison_service import compare_papers

@st.cache_data(show_spinner=False)
def cached_fetch(query):
    return fetch_arxiv_papers(query)

@st.cache_resource
def cached_load_paper(paper_id):
    return load_paper(paper_id)

def extract_arxiv_id(input_text):
    input_text = input_text.strip()
    if "arxiv.org" in input_text:
        return input_text.strip().split("/")[-1]
    return input_text

st.set_page_config(page_title="AI Paper Simplifier", layout="wide")

# ---------------- CSS ----------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0E1117, #1A1D24);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0E1117, #151922);
}

[data-testid="stSidebar"] * {
    color: #E5E7EB !important;
}

label, p, span {
    color: #E5E7EB !important;
}

textarea, input {
    color: #111827 !important;
}

textarea {
    background-color: #F9FAFB !important;
}

.section {
    background: rgba(255,255,255,0.08);
    padding: 20px;
    border-radius: 14px;
}

button {
    border-radius: 10px !important;
    background: linear-gradient(90deg, #6C63FF, #00C9A7) !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("<h1 style='text-align:center;'>AI Research Paper Simplifier</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Understand research papers effortlessly using AI</p>", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "paper_store" not in st.session_state:
    st.session_state.paper_store = {}

if "compare" not in st.session_state:
    st.session_state.compare = None

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title(" Settings")

    mode = st.selectbox("Explanation Style", ["Simple", "Normal", "Technical"])

# ---------------- LAYOUT ----------------
col1, col2 = st.columns(2)

# ================= LEFT =================
with col1:
    st.subheader(" Load Paper")

    tab1, tab2 = st.tabs([" Search Papers", " Enter ID / URL"])

    # -------- SEARCH --------
    with tab1:
        query = st.text_input("Search Papers")

        if st.button("Search"):
            st.session_state.papers = cached_fetch(query)

        papers = st.session_state.get("papers", [])

        if papers:
            titles = [p['title'] for p in papers]
            selected_title = st.selectbox("Select Paper", titles)

            selected_paper = papers[titles.index(selected_title)]

            if st.button("Process Selected Paper"):
                paper_id = selected_paper['url'].split('/')[-1]

                index, chunks = cached_load_paper(paper_id)

                st.session_state.paper_store[paper_id] = {
                    "index": index,
                    "chunks": chunks
                }

                st.session_state.index = index
                st.session_state.chunks = chunks
                st.success("Paper loaded!")

    # -------- ID --------
    with tab2:
        paper_input = st.text_input("Enter arXiv ID or URL")

        if st.button("Process Paper"):
            paper_id = extract_arxiv_id(paper_input)

            file_path = download_pdf(paper_id)
            text = extract_text(file_path)
            index, chunks = process_paper(text)

            st.session_state.paper_store[paper_id] = {
                "index": index,
                "chunks": chunks
            }

            st.session_state.index = index
            st.session_state.chunks = chunks
            st.success("Paper loaded!")

    # -------- COMPARISON SELECTOR --------
    if st.session_state.paper_store:
        st.markdown("---")
        st.markdown("##  Stored Papers")

        paper_ids = list(st.session_state.paper_store.keys())

        selected = st.multiselect("Select any 2 papers", paper_ids, max_selections=2)

        if len(selected) == 2:
            if st.button(" Compare Papers"):
                st.session_state.compare = selected

# ================= RIGHT =================
with col2:
    st.subheader(" Chat with Paper")

    # -------- COMPARISON OUTPUT --------
    if st.session_state.compare:
        p1, p2 = st.session_state.compare

        result = compare_papers(
            st.session_state.paper_store[p1],
            st.session_state.paper_store[p2],
            mode
        )

        st.markdown("##  Paper Comparison")

        sections = result.split("\n\n")

        for sec in sections:
            st.markdown(
                f"""
                <div style='
                background: rgba(255,255,255,0.06);
                padding: 16px;
                border-radius: 12px;
                margin-bottom: 12px;
                color: #F9FAFB;
                '>
                {sec}
                </div>
                """,
                unsafe_allow_html=True
            )

    # -------- CHAT --------
    if "index" in st.session_state:

        if st.button(" Summarize Paper"):
            summary, sources = summarize_paper(
                st.session_state.index,
                st.session_state.chunks,
                mode
            )

            st.session_state.messages.append({
                "role": "assistant",
                "content": summary,
                "sources": sources
            })

        user_input = st.chat_input("Ask something...")

        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})

            answer, sources = answer_question(
                user_input,
                st.session_state.index,
                st.session_state.chunks,
                mode
            )

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources
            })

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    else:
        st.info("Load a paper to begin.")