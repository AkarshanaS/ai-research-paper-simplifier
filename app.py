import streamlit as st
from src.arxiv_fetcher import fetch_arxiv_papers
from src.pdf_downloader import download_pdf
from src.text_extractor import extract_text
from src.main import process_paper, answer_question, summarize_paper
from services.paper_service import load_paper
from services.comparison_service import compare_papers
import html

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

:root {
    --bg:         #0D1117;
    --surface:    #161B26;
    --surface2:   #1C2232;
    --border:     #263048;
    --accent:     #E8A830;
    --text:       #D8DCE8;
    --text-muted: #6A738A;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stSidebar"] { display: none; }

/* ── Hide Streamlit toolbar clutter (contrast_mode, theme switcher, etc.) ── */
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
header[data-testid="stHeader"],
#MainMenu,
footer { display: none !important; }

/* ── Custom chat bubbles ── */
.chat-bubble {
    display: flex;
    gap: 10px;
    align-items: flex-start;
    margin-bottom: 14px;
}

.chat-bubble.user { flex-direction: row-reverse; }

.chat-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 15px;
    flex-shrink: 0;
    border: 1px solid var(--border);
}

.chat-avatar.user-av { background: var(--surface2); }
.chat-avatar.bot-av  { background: rgba(232,168,48,0.12); border-color: rgba(232,168,48,0.3); }

.chat-body {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 12px 16px;
    max-width: 85%;
    font-size: 14px;
    line-height: 1.7;
    color: var(--text);
}

.chat-bubble.user .chat-body {
    background: var(--surface2);
}

[data-testid="stMainBlockContainer"] {
    padding: 2rem 3rem;
    max-width: 1200px;
    margin: 0 auto;
}

h1, h2, h3 {
    font-family: 'Instrument Serif', serif !important;
    color: var(--text) !important;
    font-weight: 400 !important;
}

p, label, span, div {
    font-family: 'DM Sans', sans-serif !important;
    color: var(--text) !important;
}

.paperlens-header {
    display: flex;
    align-items: baseline;
    gap: 12px;
    border-bottom: 1px solid var(--border);
    padding-bottom: 1rem;
    margin-bottom: 2.5rem;
}

.paperlens-wordmark {
    font-family: 'Instrument Serif', serif;
    font-size: 28px;
    color: var(--accent);
    letter-spacing: -0.5px;
}

.paperlens-tagline {
    font-size: 13px;
    color: var(--text-muted);
    font-style: italic;
    font-family: 'Instrument Serif', serif !important;
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    padding: 10px 14px !important;
    box-shadow: none !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(232,168,48,0.15) !important;
}

.stSelectbox > div > div {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
}

.stButton > button {
    background: var(--accent) !important;
    color: #0D1117 !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 10px 20px !important;
    letter-spacing: 0.3px !important;
    transition: background 0.15s ease !important;
}

.stButton > button p,
.stButton > button span,
.stButton > button div {
    color: #0D1117 !important;
    font-weight: 500 !important;
}

.stButton > button:hover { background: #F5B830 !important; }

.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    color: var(--text-muted) !important;
    background: transparent !important;
    border: none !important;
    padding: 8px 18px !important;
    font-weight: 400 !important;
}

.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    font-weight: 500 !important;
    border-bottom: 2px solid var(--accent) !important;
}

.section-label {
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 12px;
}

.paper-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 12px;
    color: var(--text-muted);
    margin: 4px 4px 4px 0;
}

.compare-table { width: 100%; border-collapse: collapse; font-size: 13px; }

.compare-table th {
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    color: var(--text-muted);
    padding: 10px 14px;
    text-align: left;
    border-bottom: 1px solid var(--border);
    background: var(--surface2);
}

.compare-table td {
    padding: 14px;
    vertical-align: top;
    border-bottom: 1px solid var(--border);
    color: var(--text);
    line-height: 1.65;
}

.compare-table td:first-child {
    font-weight: 500;
    color: var(--accent);
    width: 20%;
    white-space: nowrap;
}

.compare-table tr:last-child td { border-bottom: none; }
.compare-table tr:hover td { background: rgba(232,168,48,0.03); }

.source-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid var(--border);
}

.source-chip {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 11px;
    color: var(--accent);
    font-family: 'DM Sans', sans-serif;
    letter-spacing: 0.3px;
}

.summary-box {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 0 12px 12px 0;
    padding: 20px 22px;
    margin-bottom: 20px;
}

.summary-box-label {
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 10px;
}

.summary-box p, .summary-box li {
    font-size: 14px !important;
    line-height: 1.75 !important;
    color: var(--text) !important;
}

.stChatMessage {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}

/* Hide Material icon avatars, collapse the wasted column */
[data-testid="chatAvatarIcon-user"],
[data-testid="chatAvatarIcon-assistant"] { display: none !important; }

[data-testid="stChatMessage"] > div:first-child {
    min-width: 0 !important;
    width: 0 !important;
    overflow: hidden !important;
    padding: 0 !important;
}

[data-testid="stChatMessageContent"] p {
    font-size: 14px !important;
    line-height: 1.7 !important;
    color: var(--text) !important;
}

[data-testid="stChatInput"] > div {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}

[data-testid="stChatInput"] textarea {
    color: var(--text) !important;
    background: transparent !important;
}

.stSuccess > div {
    background: rgba(50,180,80,0.08) !important;
    border: 1px solid rgba(50,180,80,0.25) !important;
    border-radius: 8px !important;
    color: #7ED99A !important;
}

.stInfo > div {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text-muted) !important;
}

.stMultiSelect > div > div {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}

hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 1.5rem 0 !important;
}

.stSpinner > div { border-top-color: var(--accent) !important; }
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
            """Strip markdown bold/italic/heading markers."""
            text = re.sub(r'\*{1,2}(.*?)\*{1,2}', r'\1', text)
            text = re.sub(r'^#{1,4}\s*', '', text)
            return text.strip()

        # Split on blank lines — works regardless of whether sections
        # start with letters, *, #, or any other character.
        rows = []
        sections = re.split(r'\n\s*\n', result.strip())
        for sec in sections:
            raw_lines = [l.strip() for l in sec.strip().splitlines() if l.strip()]
            if not raw_lines:
                continue
            heading = clean(raw_lines[0]).rstrip(":")
            # Skip if heading looks like a stray bullet rather than a real section title
            if heading.lower().startswith("paper"):
                continue
            p1_text, p2_text = "", ""
            for line in raw_lines[1:]:
                line_clean = clean(line).lstrip("-–•* ").strip()
                lo = line_clean.lower()
                if lo.startswith("paper 1:"):
                    p1_text = line_clean[8:].strip()
                elif lo.startswith("paper 2:"):
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
            <div style="background:var(--surface);border:1px solid var(--border);border-radius:12px;overflow:hidden;margin-bottom:20px;">
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
            # Fallback: render cleaned plain text if parsing yields nothing
            st.markdown(
                f'<div style="font-size:14px;line-height:1.7;color:var(--text);">{clean(result)}</div>',
                unsafe_allow_html=True
            )

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
                <div style="font-size:14px;line-height:1.75;color:var(--text);">
                    {st.session_state.summary}
                </div>
                <div class="source-bar">{chips}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # ── CHAT (separate section) ──
        st.markdown('<p class="section-label">Ask the paper</p>', unsafe_allow_html=True)

        for msg in st.session_state.messages:
            role = msg["role"]
            bubble_class = "user" if role == "user" else "assistant"
            avatar_class  = "user-av" if role == "user" else "bot-av"
            avatar_icon   = "👤" if role == "user" else "🔬"

            source_html = ""
            if role == "assistant" and msg.get("sources"):
                pages = sorted(set(c["page"] for c in msg["sources"] if "page" in c))
                chips = "".join(f'<span class="source-chip">p. {p}</span>' for p in pages)
                source_html = f'<div class="source-bar">{chips}</div>'
            
            safe_content =  html.escape(msg["content"])

            st.markdown(f"""
            <div class="chat-bubble {bubble_class}">
                <div class="chat-avatar {avatar_class}">{avatar_icon}</div>
                <div class="chat-body">
                    )
                    {safe_content}
                    {source_html}
                </div>
            </div>
            """, unsafe_allow_html=True)

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