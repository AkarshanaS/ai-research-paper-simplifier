import streamlit as st
from src.arxiv_fetcher import fetch_arxiv_papers
from src.pdf_downloader import download_pdf
from src.text_extractor import extract_text
from src.main import process_paper, answer_question
from src.llm import generate_answer

#page config
st.set_page_config(page_title="AI Paper Simplifier", layout="wide")

#custom CSS for styling
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

/* Section (Glass) */
.section {
    background: rgba(255, 255, 255, 0.06);
    padding: 22px;
    border-radius: 16px;
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.08);
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

/* Inputs */
input, textarea {
    background-color: rgba(255,255,255,0.08) !important;
    color: white !important;
    border-radius: 10px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
}

/* Dropdown */
div[data-baseweb="select"] {
    background-color: rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
}

/* Buttons */
button {
    border-radius: 10px !important;
    background: linear-gradient(90deg, #6C63FF, #00C9A7) !important;
    color: white !important;
    border: none !important;
}

/* Chat bubbles */
.chat-user {
    background: rgba(108, 99, 255, 0.2);
    padding: 10px;
    border-radius: 10px;
}

.chat-bot {
    background: rgba(255, 255, 255, 0.08);
    padding: 10px;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

#header
st.markdown('<div class="main-title">AI Research Paper Simplifier</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Understand research papers effortlessly using AI</div>', unsafe_allow_html=True)

#session state
if "messages" not in st.session_state:
    st.session_state.messages = []

#sidebar settings
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

# ---------------------------
# LAYOUT
# ---------------------------
col1, col2 = st.columns([1, 2])

#left panel - paper search and processing
with col1:
    st.markdown('<div class="section">', unsafe_allow_html=True)

    st.subheader("🔍 Search Papers")
    query = st.text_input("Search for research papers")

    st.markdown("<br>", unsafe_allow_html=True)

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

                # Metrics
                st.metric("Chunks", len(chunks))
                st.metric("Embedding Dim", len(index[0]))

    st.markdown('</div>', unsafe_allow_html=True)

#right panel - chat interface
with col2:
    st.markdown('<div class="section">', unsafe_allow_html=True)

    st.subheader("💬 Chat with Paper")

    if "index" in st.session_state:

        # Summary
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

        # Chat display
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
        <div style='padding:20px;
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
        text-align:center;'>
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