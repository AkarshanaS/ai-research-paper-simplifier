import streamlit as st
from src.arxiv_fetcher import fetch_arxiv_papers
from src.pdf_downloader import download_pdf
from src.text_extractor import extract_text
from src.main import process_paper, answer_question, summarize_paper
from src.llm import generate_answer

def extract_arxiv_id(input_text):
    input_text = input_text.strip()
    if "arxiv.org" in input_text:
        return input_text.strip().split("/")[-1]
    return input_text

#page config
st.set_page_config(page_title="AI Paper Simplifier", layout="wide")

#custom CSS
st.markdown("""
<style>

/* Background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0E1117, #1A1D24);
    color: white;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0E1117, #151922);
    border-right: 1px solid rgba(255,255,255,0.05);
}

/* Sidebar text */
[data-testid="stSidebar"] * {
    color: rgba(255,255,255,0.85) !important;
}

/* Section */
.section {
    background: rgba(255, 255, 255, 0.05);
    padding: 22px;
    border-radius: 16px;
    backdrop-filter: blur(12px);
    margin-bottom: 25px;
}

/* Title */
.main-title {
    text-align: center;
    font-size: 44px;
    font-weight: bold;
    background: linear-gradient(90deg, #6C63FF, #00C9A7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0px 0px 20px rgba(108, 99, 255, 0.4);
}

/* Subtitle */
.subtitle {
    text-align: center;
    color: #9CA3AF;
    margin-bottom: 35px;
}

/* Input */

/* Remove outer container background */
div[data-baseweb="input"] {
    background: transparent !important;
    box-shadow: none !important;
}

/* Style */
div[data-baseweb="input"] > div {
    background-color: rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    padding: 6px !important;
    max-width: 95%;
}

/* Input text */
div[data-baseweb="input"] input {
    background-color: transparent !important;
    color: white !important;
}

/* Placeholder */
input::placeholder {
    color: rgba(255,255,255,0.5) !important;
}

/* DROPDOWN */
div[data-baseweb="select"] > div {
    background-color: rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
    color: white !important;
}

/* CHAT INPUT */
textarea {
    background-color: rgba(255,255,255,0.08) !important;
    color: white !important;
}

/* Buttons */
button {
    border-radius: 12px !important;
    background: linear-gradient(90deg, #6C63FF, #00C9A7) !important;
    color: white !important;
    border: none !important;
    font-weight: 600 !important;
    padding: 8px 16px !important;
}

button:hover {
    transform: scale(1.03);
    transition: 0.2s ease;
}

</style>
""", unsafe_allow_html=True)

#header
st.markdown('<div class="main-title">AI Research Paper Simplifier</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Understand research papers effortlessly using AI</div>', unsafe_allow_html=True)

#session state
if "messages" not in st.session_state:
    st.session_state.messages = []

#sidebar
with st.sidebar:
    st.title("📄 Summarize Paper")

    mode = st.selectbox(
        "Explanation Style",
        ["Simple", "Normal", "Technical"]
    )

    st.markdown("### 💡 Example Questions")
    st.write("• Why does this research matter?")
    st.write("• What is the 'big idea' here?")
    st.write("• Explain the math in Section 3")

    st.markdown("---")
    st.caption("Built with RAG + OpenAI + Cosine Similarity")

#layout
col1, col2 = st.columns(2)  # equal width 

#left panel
with col1:
    st.subheader("🔍 Load Paper")

    # Initialize session state
    if "papers" not in st.session_state:
        st.session_state.papers = []

    if "selected_paper" not in st.session_state:
        st.session_state.selected_paper = None

    input_type = st.radio(
        "Choose Input Method",
        ["Search Papers", "Enter arXiv ID / URL"]
    )

    if input_type == "Search Papers":
        query = st.text_input("Search Papers", placeholder="e.g. transformers")

        if st.button("🔍 Search"):
            if query:
                if "last_query" not in st.session_state or st.session_state.last_query != query:
                    with st.spinner("Searching papers..."):
                        st.session_state.papers = fetch_arxiv_papers(query)
                        st.session_state.last_query = query

        papers = st.session_state.papers

        if papers:
            titles = [p['title'] for p in papers]
            selected_title = st.selectbox("Select a paper", titles)

            st.session_state.selected_paper = papers[titles.index(selected_title)]

            if st.button("Process Paper"):
                paper = st.session_state.selected_paper
                paper_id = paper['url'].split('/')[-1]

                with st.spinner("Processing paper..."):
                    file_path = download_pdf(paper_id)
                    text = extract_text(file_path)

                    index, chunks = process_paper(text)

                    st.session_state.index = index
                    st.session_state.chunks = chunks
                    st.session_state.messages = []

                st.success("✅ Paper ready!")
                st.metric("Chunks", len(chunks))
                st.metric("Embedding Dim", len(index[0]))

    #id/url mode
    else:
        paper_input = st.text_input(
            "Enter arXiv ID or URL",
            placeholder="e.g. 1706.03762 or https://arxiv.org/abs/1706.03762"
        )

        if st.button("Process Paper"):
            if paper_input:
                paper_id = extract_arxiv_id(paper_input)

                with st.spinner("Processing paper..."):
                    file_path = download_pdf(paper_id)
                    text = extract_text(file_path)

                    index, chunks = process_paper(text)

                    st.session_state.index = index
                    st.session_state.chunks = chunks
                    st.session_state.messages = []

                st.success("✅ Paper ready!")
                st.metric("Chunks", len(chunks))
                st.metric("Embedding Dim", len(index[0]))

#right panel
with col2:
    st.subheader("💬 Chat with Paper")

    if "index" in st.session_state:
        
        if st.button("📄 Summarize Paper"):
            with st.spinner("Generating summary..."):
                summary, sources = summarize_paper(
                    st.session_state.index,
                    st.session_state.chunks,
                    mode = mode
                )
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": summary,
                "sources": sources
                })

        user_input = st.chat_input("Ask something about the paper...")

        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})

            with st.spinner("Thinking..."):
                answer, sources = answer_question(
                    user_input,
                    st.session_state.index,
                    st.session_state.chunks,
                    mode = mode
                )

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources
            })

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

                if msg["role"] == "assistant" and "sources" in msg:
                    with st.expander("📚 Sources & Citationss"):
                        for i, s in enumerate(msg["sources"]):
                            st.markdown(f"**Source {i+1} — Page {s['page']}**")
                            st.caption(s['text'])
                            st.divider()

    else:
        st.markdown("""
        <div style='padding:22px;
        background: linear-gradient(90deg, rgba(108,99,255,0.15), rgba(0,201,167,0.1));
        border-radius: 14px;
        text-align:center;
        font-size:16px;'>
        💬 Ask anything about the paper once it's loaded
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

#footer
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:gray;'>Built with ❤️ using RAG + OpenAI</p>",
    unsafe_allow_html=True
)