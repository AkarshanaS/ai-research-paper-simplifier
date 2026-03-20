import streamlit as st
from src.arxiv_fetcher import fetch_arxiv_papers
from src.pdf_downloader import download_pdf
from src.text_extractor import extract_text
from src.main import process_paper, answer_question

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="AI Paper Simplifier", layout="wide")

# ---------------------------
# CUSTOM CSS (Premium Look)
# ---------------------------
st.markdown("""
<style>
body {
    background-color: #0E1117;
}
.main-title {
    text-align: center;
    color: #6C63FF;
    font-size: 42px;
    font-weight: bold;
}
.subtitle {
    text-align: center;
    font-size: 18px;
    color: #AAAAAA;
    margin-bottom: 30px;
}
.card {
    background-color: #1C1F26;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# HEADER
# ---------------------------
st.markdown('<div class="main-title"> AI Research Paper Simplifier</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Understand research papers effortlessly using AI</div>', unsafe_allow_html=True)

# ---------------------------
# SESSION STATE
# ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------
# SIDEBAR
# ---------------------------
with st.sidebar:
    st.title("Settings")

    st.markdown("### 💡 Tips")
    st.write("• Ask specific questions")
    st.write("• Try 'Explain simply'")
    st.write("• Ask about methodology/results")

    st.markdown("---")
    st.write("Built with RAG + OpenAI + FAISS")

# ---------------------------
# LAYOUT
# ---------------------------
col1, col2 = st.columns([1, 2])

# ---------------------------
# LEFT PANEL (Search)
# ---------------------------
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Search Papers")

    query = st.text_input("Search for research papers")

    if query:
        papers = fetch_arxiv_papers(query)

        if papers:
            titles = [p['title'] for p in papers]
            selected = st.selectbox("Select a paper", titles)

            if st.button("Process Paper"):
                paper = papers[titles.index(selected)]
                paper_id = paper['url'].split('/')[-1]

                with st.spinner("Downloading & processing..."):
                    file_path = download_pdf(paper_id)
                    text = extract_text(file_path)

                    index, model, chunks = process_paper(text)

                    st.session_state.index = index
                    st.session_state.model = model
                    st.session_state.chunks = chunks
                    st.session_state.messages = []

                st.success("✅ Paper processed successfully!")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# RIGHT PANEL (Chat)
# ---------------------------
with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("💬 Ask Questions")

    if "index" in st.session_state:

        user_input = st.chat_input("Ask something about the paper...")

        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})

            with st.spinner("Thinking..."):
                answer, sources = answer_question(
                    user_input,
                    st.session_state.index,
                    st.session_state.model,
                    st.session_state.chunks
                )

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources
            })

        # CHAT DISPLAY
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

                if msg["role"] == "assistant" and "sources" in msg:
                    st.markdown("### Sources")
                    for i, s in enumerate(msg["sources"]):
                        with st.expander(f"Source {i+1}"):
                            st.write(s)

    else:
        st.info("👈 Search and process a paper first")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# FOOTER
# ---------------------------
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:gray;'>Built with ❤️ using RAG + OpenAI</p>",
    unsafe_allow_html=True
)