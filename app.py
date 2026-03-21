import streamlit as st
from src.arxiv_fetcher import fetch_arxiv_papers
from src.pdf_downloader import download_pdf
from src.text_extractor import extract_text
from src.main import process_paper, answer_question
from src.llm import generate_answer

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
    color: rgba(255,255,255,0.85);
}

/* Sidebar text */
[data-testid="stSidebar"] * {
    color: rgba(255,255,255,0.85) !important;
}

/* Section */
.section {
    background: rgba(255, 255, 255, 0.06);
    padding: 22px;
    border-radius: 16px;
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 25px;
    height: 100%;
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

/* INPUT */
div[data-baseweb="input"] > div {
    background-color: rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
}

div[data-baseweb="input"] input {
    background-color: transparent !important;
    color: white !important;
}

/* DROPDOWN FIX */
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
    st.title("⚙️ Settings")

    mode = st.selectbox(
        "Explanation Style",
        ["Simple", "Normal", "Technical"]
    )

    st.markdown("### 💡 Example Questions")
    st.write("• Explain this paper simply")
    st.write("• What problem does it solve?")
    st.write("• What are key contributions?")

    st.markdown("---")
    st.caption("Built with RAG + OpenAI + Cosine Similarity")

#layout
col1, col2 = st.columns(2)  # equal width now

#left panel
with col1:
    st.markdown('<div class="section">', unsafe_allow_html=True)

    st.subheader("🔍 Search Papers")
    query = st.text_input("Search for research papers")

    if query:
        papers = fetch_arxiv_papers(query)

        if papers:
            titles = [p['title'] for p in papers]
            selected = st.selectbox("Select a paper", titles)

            if st.button("🚀 Process Paper"):
                paper = papers[titles.index(selected)]
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

    st.markdown('</div>', unsafe_allow_html=True)

#right panel
with col2:
    st.markdown('<div class="section">', unsafe_allow_html=True)

    st.subheader("💬 Chat with Paper")

    if "index" in st.session_state:

        if st.button("📄 Summarize Paper"):
            with st.spinner("Generating summary..."):
                summary = generate_answer(
                    "Summarize this paper in simple terms",
                    st.session_state.chunks[:5]
                )
            st.success(summary)

        user_input = st.chat_input("Ask something about the paper...")

        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})

            if mode == "Simple":
                user_input = "Explain simply: " + user_input
            elif mode == "Technical":
                user_input = "Give a detailed technical explanation: " + user_input

            with st.spinner("Thinking..."):
                answer, sources = answer_question(
                    user_input,
                    st.session_state.index,
                    st.session_state.chunks
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
                    with st.expander("📚 Sources"):
                        for i, s in enumerate(msg["sources"]):
                            st.write(f"**Chunk {i+1}:**")
                            st.write(s)

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