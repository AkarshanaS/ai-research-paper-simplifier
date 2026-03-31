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

st.set_page_config(page_title="PaperLens", layout="wide", page_icon="🔬")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Reset & Base ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #F5F2EE !important;
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stSidebar"] { display: none; }

[data-testid="stMainBlockContainer"] {
    padding: 2rem 3rem;
    max-width: 1200px;
    margin: 0 auto;
}

/* ── Typography ── */
h1, h2, h3 {
    font-family: 'Instrument Serif', serif !important;
    color: #1C1916 !important;
    font-weight: 400 !important;
}

p, label, span, div {
    font-family: 'DM Sans', sans-serif !important;
    color: #3D3A35 !important;
}

/* ── Header ── */
.paperlens-header {
    display: flex;
    align-items: baseline;
    gap: 12px;
    border-bottom: 1.5px solid #1C1916;
    padding-bottom: 1rem;
    margin-bottom: 2.5rem;
}

.paperlens-wordmark {
    font-family: 'Instrument Serif', serif;
    font-size: 28px;
    color: #1C1916;
    letter-spacing: -0.5px;
}

.paperlens-tagline {
    font-size: 13px;
    color: #8A8278;
    font-style: italic;
    font-family: 'Instrument Serif', serif !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #FDFBF8 !important;
    border: 1px solid #C9C4BC !important;
    border-radius: 8px !important;
    color: #1C1916 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    padding: 10px 14px !important;
    box-shadow: none !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #6B5B3E !important;
    box-shadow: 0 0 0 3px rgba(107, 91, 62, 0.12) !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: #FDFBF8 !important;
    border: 1px solid #C9C4BC !important;
    border-radius: 8px !important;
    color: #1C1916 !important;
}

/* ── Buttons ── */
.stButton > button {
    background: #1C1916 !important;
    color: #F5F2EE !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 10px 20px !important;
    letter-spacing: 0.3px !important;
    transition: background 0.15s ease !important;
}

/* Streamlit wraps button text in p/span — override those too */
.stButton > button p,
.stButton > button span,
.stButton > button div {
    color: #F5F2EE !important;
    font-weight: 500 !important;
}

.stButton > button:hover {
    background: #3D3A35 !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #C9C4BC !important;
    gap: 0 !important;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    color: #8A8278 !important;
    background: transparent !important;
    border: none !important;
    padding: 8px 18px !important;
    font-weight: 400 !important;
}

.stTabs [aria-selected="true"] {
    color: #1C1916 !important;
    font-weight: 500 !important;
    border-bottom: 2px solid #1C1916 !important;
}

/* ── Cards ── */
.paper-card {
    background: #FDFBF8;
    border: 1px solid #DDD9D3;
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 10px;
}

.paper-card-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 14px;
    font-weight: 500;
    color: #1C1916;
    margin-bottom: 4px;
}

.paper-card-meta {
    font-size: 12px;
    color: #8A8278;
}

/* ── Section header ── */
.section-label {
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #8A8278;
    margin-bottom: 12px;
}

/* ── Loaded paper pill ── */
.paper-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #EAE7E2;
    border-radius: 20px;
    padding: 5px 12px;
    font-size: 12px;
    color: #3D3A35;
    margin: 4px 4px 4px 0;
}

/* ── Comparison table ── */
.compare-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    margin-top: 8px;
}

.compare-table th {
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    color: #8A8278;
    padding: 8px 12px;
    text-align: left;
    border-bottom: 1px solid #DDD9D3;
}

.compare-table td {
    padding: 14px 12px;
    vertical-align: top;
    border-bottom: 1px solid #EAE7E2;
    color: #3D3A35;
    line-height: 1.65;
}

.compare-table td:first-child {
    font-weight: 500;
    color: #1C1916;
    width: 22%;
    white-space: nowrap;
}

.compare-table tr:last-child td {
    border-bottom: none;
}

.compare-table tr:hover td {
    background: rgba(28,25,22,0.02);
}

/* ── Source citation chips ── */
.source-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid #EAE7E2;
}

.source-chip {
    background: #EAE7E2;
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 11px;
    color: #5C5850;
    font-family: 'DM Sans', sans-serif;
}

/* ── Summary box ── */
.summary-box {
    background: #FDFBF8;
    border: 1px solid #DDD9D3;
    border-left: 3px solid #1C1916;
    border-radius: 0 12px 12px 0;
    padding: 20px 22px;
    margin-bottom: 20px;
}

.summary-box-label {
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #8A8278;
    margin-bottom: 10px;
}

.summary-box p, .summary-box li {
    font-size: 14px !important;
    line-height: 1.75 !important;
    color: #3D3A35 !important;
}

/* ── Chat ── */
.stChatMessage {
    background: #FDFBF8 !important;
    border: 1px solid #EAE7E2 !important;
    border-radius: 12px !important;
}

[data-testid="stChatMessageContent"] p {
    font-size: 14px !important;
    line-height: 1.7 !important;
}

/* ── Success / Info ── */
.stSuccess {
    background: #EDF5EC !important;
    border: 1px solid #B6D9B2 !important;
    border-radius: 8px !important;
    color: #1E4D1B !important;
}

.stInfo {
    background: #EAE7E2 !important;
    border: 1px solid #C9C4BC !important;
    border-radius: 8px !important;
    color: #3D3A35 !important;
}

/* ── Multiselect ── */
.stMultiSelect > div > div {
    background: #FDFBF8 !important;
    border: 1px solid #C9C4BC !important;
    border-radius: 8px !important;
}

/* ── Divider ── */
hr {
    border: none !important;
    border-top: 1px solid #DDD9D3 !important;
    margin: 1.5rem 0 !important;
}

/* ── Subheader override ── */
.stSubheader {
    font-family: 'Instrument Serif', serif !important;
    font-size: 20px !important;
    font-weight: 400 !important;
    color: #1C1916 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Header ──
st.markdown("""
<div class="paperlens-header">
    <span class="paperlens-wordmark">PaperLens</span>
    <span class="paperlens-tagline">read less, understand more</span>
</div>
""", unsafe_allow_html=True)

# ── Mode selector (top right) ──
col_spacer, col_mode = st.columns([4, 1])
with col_mode:
    mode = st.selectbox("Explanation style", ["Simple", "Normal", "Technical"], label_visibility="collapsed")

# ── Session state ──
if "messages" not in st.session_state:
    st.session_state.messages = []
if "paper_store" not in st.session_state:
    st.session_state.paper_store = {}
if "compare" not in st.session_state:
    st.session_state.compare = None

# ── Two-column layout ──
col1, col2 = st.columns([1, 1], gap="large")

# ═══════════════ LEFT PANEL ═══════════════
with col1:
    st.markdown('<p class="section-label">Load a paper</p>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Search arXiv", "Enter ID or URL"])

    with tab1:
        query = st.text_input("Search query", placeholder="e.g. attention is all you need", label_visibility="collapsed")
        if st.button("Search", key="search_btn"):
            with st.spinner("Searching arXiv…"):
                st.session_state.papers = cached_fetch(query)

        papers = st.session_state.get("papers", [])
        if papers:
            titles = [p['title'] for p in papers]
            selected_title = st.selectbox("Results", titles, label_visibility="collapsed")
            selected_paper = papers[titles.index(selected_title)]

            if st.button("Load this paper", key="load_search"):
                paper_id = selected_paper['url'].split('/')[-1]
                with st.spinner("Downloading and indexing…"):
                    try:
                        index, chunks = cached_load_paper(paper_id)
                        st.session_state.paper_store[paper_id] = {"index": index, "chunks": chunks}
                        st.session_state.index = index
                        st.session_state.chunks = chunks
                        st.success(f"Loaded · {paper_id}")
                    except Exception as e:
                        st.error(f"Failed to load paper: {e}")

    with tab2:
        paper_input = st.text_input("arXiv ID or URL", placeholder="2301.07041 or arxiv.org/abs/…", label_visibility="collapsed")
        if st.button("Load paper", key="load_id"):
            paper_id = extract_arxiv_id(paper_input)
            with st.spinner("Downloading and indexing…"):
                try:
                    file_path = download_pdf(paper_id)
                    text = extract_text(file_path)
                    index, chunks = process_paper(text)
                    st.session_state.paper_store[paper_id] = {"index": index, "chunks": chunks}
                    st.session_state.index = index
                    st.session_state.chunks = chunks
                    st.success(f"Loaded · {paper_id}")
                except Exception as e:
                    st.error(f"Failed to load paper: {e}")

    # ── Loaded papers ──
    if st.session_state.paper_store:
        st.markdown("---")
        st.markdown('<p class="section-label">Loaded papers</p>', unsafe_allow_html=True)

        pills_html = "".join(
            f'<span class="paper-pill">📄 {pid}</span>'
            for pid in st.session_state.paper_store
        )
        st.markdown(pills_html, unsafe_allow_html=True)

        if len(st.session_state.paper_store) >= 2:
            st.markdown("")
            st.markdown('<p class="section-label">Compare</p>', unsafe_allow_html=True)
            paper_ids = list(st.session_state.paper_store.keys())
            selected = st.multiselect("Select two papers to compare", paper_ids, max_selections=2, label_visibility="collapsed")
            if len(selected) == 2:
                if st.button("Compare papers →", key="compare_btn"):
                    st.session_state.compare = selected

import re, json

# ═══════════════ RIGHT PANEL ═══════════════
with col2:

    # ── Comparison output ──
    if st.session_state.compare:
        p1, p2 = st.session_state.compare
        st.markdown('<p class="section-label">Comparison</p>', unsafe_allow_html=True)

        if "compare_result" not in st.session_state or st.session_state.get("compare_ids") != tuple(st.session_state.compare):
            with st.spinner("Comparing papers…"):
                st.session_state.compare_result = compare_papers(
                    st.session_state.paper_store[p1],
                    st.session_state.paper_store[p2],
                    mode
                )
                st.session_state.compare_ids = tuple(st.session_state.compare)

        result = st.session_state.compare_result

        def clean(text):
            """Strip markdown bold/italic markers."""
            return re.sub(r'\*{1,2}(.*?)\*{1,2}', r'\1', text).strip()

        # Parse into rows: extract lines starting with "- Paper 1:" / "- Paper 2:"
        # The LLM returns sections separated by double newlines, each with a header + 2 bullet lines.
        rows = []
        sections = re.split(r'\n(?=\w)', result.strip())
        for sec in sections:
            lines = [l.strip() for l in sec.strip().splitlines() if l.strip()]
            if not lines:
                continue
            heading = clean(lines[0]).rstrip(":")
            p1_text, p2_text = "", ""
            for line in lines[1:]:
                line_clean = clean(line).lstrip("-• ").strip()
                if line_clean.lower().startswith("paper 1:"):
                    p1_text = line_clean[8:].strip()
                elif line_clean.lower().startswith("paper 2:"):
                    p2_text = line_clean[8:].strip()
            if heading and (p1_text or p2_text):
                rows.append((heading, p1_text, p2_text))

        if rows:
            table_rows = ""
            for label, v1, v2 in rows:
                table_rows += f"""
                <tr>
                    <td>{label}</td>
                    <td>{v1 or "—"}</td>
                    <td>{v2 or "—"}</td>
                </tr>"""

            st.markdown(f"""
            <div style="background:#FDFBF8;border:1px solid #DDD9D3;border-radius:12px;overflow:hidden;margin-bottom:20px;">
                <table class="compare-table">
                    <thead>
                        <tr>
                            <th></th>
                            <th>{p1}</th>
                            <th>{p2}</th>
                        </tr>
                    </thead>
                    <tbody>{table_rows}</tbody>
                </table>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Fallback: just render cleaned text
            st.markdown(f'<div style="font-size:14px;line-height:1.7;color:#3D3A35;">{clean(result)}</div>', unsafe_allow_html=True)

        st.markdown("---")

    # ── Paper loaded ──
    if "index" in st.session_state:

        # ── SUMMARY (separate from chat) ──
        st.markdown('<p class="section-label">Summary</p>', unsafe_allow_html=True)

        if st.button("Generate summary", key="summarize_btn"):
            with st.spinner("Reading the paper…"):
                try:
                    summary, sources = summarize_paper(
                        st.session_state.index,
                        st.session_state.chunks,
                        mode
                    )
                    st.session_state.summary = summary
                    st.session_state.summary_sources = sources
                except Exception as e:
                    st.error(f"Error: {e}")

        if "summary" in st.session_state:
            pages = sorted(set(
                c["page"] for c in st.session_state.summary_sources if "page" in c
            ))
            chips = "".join(f'<span class="source-chip">p. {p}</span>' for p in pages)
            st.markdown(f"""
            <div class="summary-box">
                <div class="summary-box-label">Summary</div>
                <div style="font-size:14px;line-height:1.75;color:#3D3A35;">
                    {st.session_state.summary}
                </div>
                <div class="source-bar">{chips}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # ── CHAT (separate section) ──
        st.markdown('<p class="section-label">Ask the paper</p>', unsafe_allow_html=True)

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg["role"] == "assistant" and msg.get("sources"):
                    pages = sorted(set(
                        c["page"] for c in msg["sources"] if "page" in c
                    ))
                    chips = "".join(f'<span class="source-chip">p. {p}</span>' for p in pages)
                    st.markdown(
                        f'<div class="source-bar">{chips}</div>',
                        unsafe_allow_html=True
                    )

        user_input = st.chat_input("Ask anything about this paper…")
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.spinner("Thinking…"):
                try:
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
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating answer: {e}")

    else:
        st.markdown("""
        <div style="margin-top:3rem;text-align:center;padding:2rem;">
            <p style="font-family:'Instrument Serif',serif;font-size:22px;color:#C9C4BC;">
                Load a paper to begin
            </p>
            <p style="font-size:13px;color:#8A8278;margin-top:6px;">
                Search arXiv or paste an ID on the left
            </p>
        </div>
        """, unsafe_allow_html=True)