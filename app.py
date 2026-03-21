import streamlit as st
from src.arxiv_fetcher import fetch_arxiv_papers
from src.pdf_downloader import download_pdf
from src.text_extractor import extract_text
from src.main import process_paper, answer_question
from src.llm import generate_answer

#Page config
st.set_page_config(page_title="AI Paper Simplifier", layout="wide")

#Custom CSS
st.markdown("""
<style>
.section {
    background: rgba(255, 255, 255, 0.03);
    padding: 18px;
    border-radius: 12px;
    backdrop-filter: blur(10px);
    margin-bottom: 20px;
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
col1, col2 = st.columns([1, 2])

#left panel (search and process)
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
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

                # Metrics
                st.metric("Chunks", len(chunks))
                st.metric("Embedding Dim", len(index[0]))

    st.markdown('</div>', unsafe_allow_html=True)

#right panel (chat interface)
with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("💬 Chat with Paper")

    if "index" in st.session_state:

        # 📄 Summary button
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

            # Modify query based on mode
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
        st.info("👈 Search and process a paper first")

    st.markdown('</div>', unsafe_allow_html=True)

#footer
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:gray;'>Built with ❤️ using RAG + OpenAI</p>",
    unsafe_allow_html=True
)