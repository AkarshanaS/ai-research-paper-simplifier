#🧠 AI Research Paper Simplifier

An AI-powered application that simplifies complex academic research using **Retrieval-Augmented Generation (RAG)**. Users can search for papers directly from arXiv, process them in real-time, and interact with the content using natural language.

🔗 **Live App:** [View on Streamlit](https://ai-research-paper-simplifier-ebbboh8duex77qdjzrwgyw.streamlit.app/)

---

## 🚀 Features
* 🔍 **Automated ArXiv Integration:** Search and fetch research papers directly using the arXiv API.
* 📄 **Dynamic PDF Processing:** Extracts and processes content on-the-fly using PyMuPDF.
* ✂️ **Intelligent Text Chunking:** Implements overlapping segments to maintain context across chunks.
* 🧠 **Semantic Retrieval:** Uses OpenAI embeddings and cosine similarity for high-accuracy context fetching.
* 💬 **Interactive Q&A:** A dedicated RAG pipeline to answer specific questions about the paper.
* 📚 **Source-Backed Answers:** Transparent responses that reference specific sections of the paper.
* 🎯 **Explanation Modes:** Toggle between *Simple*, *Normal*, and *Technical* modes to suit your expertise level.
* 🎨 **Modern UI:** Custom CSS-enhanced interface featuring glassmorphism and a split-screen layout.

---

## 🏗️ Technical Architecture (RAG Pipeline)

1.  **Ingestion:** Fetch paper metadata and PDF via ArXiv API.
2.  **Processing:** Extract text and partition into $k$ overlapping chunks.
3.  **Embedding:** Transform text chunks into high-dimensional vectors via OpenAI Embeddings.
4.  **Retrieval:** Compute **Cosine Similarity** between the user query vector and the document's vector space.
5.  **Augmentation:** Inject the top $N$ relevant chunks into the LLM prompt.
6.  **Generation:** OpenAI LLM generates a simplified response based strictly on the retrieved context.

---

## 🛠️ Tech Stack
* **Frontend:** Streamlit (Custom CSS)
* **LLM:** OpenAI GPT Models
* **Embeddings:** OpenAI `text-embedding-3-small` (or equivalent)
* **Vector Search:** Cosine Similarity (Manual implementation for deployment stability)
* **PDF Processing:** PyMuPDF (fitz)

---

## ⚙️ Installation & Setup

### Prerequisites
* Python 3.9+
* OpenAI API Key

### Local Setup
1. **Clone the repository:**
   ```bash
    git clone https://github.com/your-username/ai-research-paper-simplifier.git
    cd ai-research-paper-simplifier
    pip install -r requirements.txt
2. **Install dependencies:**
    '''bash
    pip install -r requirements.txt

3. **Configure Environment Variables:**
    OPENAI_API_KEY=your_api_key_here

4. **Run the app:**
    '''bash
    streamlit run app.py

## 💥 Challenges & Solutions

Building a production-ready RAG application involves more than just connecting an API. Below are the key technical hurdles I encountered and how I engineered solutions for them:

### 🛠️ Dependency & Deployment Optimization
*   **Challenge:** Faced significant compatibility issues with **FAISS** (Facebook AI Similarity Search) when deploying to Streamlit Cloud due to shared library dependencies.
*   **Solution:** Since the tool processes individual papers (medium-scale data), I replaced FAISS with a custom **Numpy-based Cosine Similarity** implementation. This eliminated the heavy dependency while maintaining sub-second retrieval speeds.

### 🔄 Embedding Pipeline Consistency
*   **Challenge:** Encountered "hallucination" issues where the LLM couldn't find answers despite them being in the text. This was traced to a mismatch between how chunks were indexed and how the query was embedded.
*   **Solution:** Standardized the pipeline by centralizing the embedding logic. I ensured that both the document chunks and the user queries utilize the same normalization and `text-embedding-3-small` model parameters.

### 📜 PDF Parsing & Context Window Management
*   **Challenge:** Research papers often contain complex layouts (multi-column text, headers, and footers) that break the flow of sentences when extracted.
*   **Solution:** Implemented **Intelligent Chunking with Overlap** (approx. 10-15% overlap). This ensures that if a key concept is split across two chunks, the semantic context is preserved, allowing the LLM to "see" the full picture.

### 🎨 UI/UX Refinement
*   **Challenge:** Default Streamlit components appeared as "white boxes" that clashed with a dark/modern theme, and the layout felt cluttered during long Q&A sessions.
*   **Solution:** 
    *   Injected **Custom CSS** to override component styling, implementing a **Glassmorphism** effect for a premium feel.
    *   Developed a **Split-Screen Layout** to separate the paper's metadata (Left) from the interactive Chat interface (Right), optimizing the user's focus.

### 🔑 Secure Secret Management
*   **Challenge:** Managing OpenAI API keys securely without hardcoding them in the repository.
*   **Solution:** Integrated **Streamlit Secrets** (`.streamlit/secrets.toml`) for cloud deployment and `.env` files for local development, ensuring SOC2-compliant style data security practices.

## 🚀 Future Roadmap

To evolve this from a single-paper assistant into a comprehensive research workstation, the following enhancements are planned:

* **📊 Multi-Paper Comparative Analysis:** Enable users to select multiple papers and generate a synthesized comparison of their methodologies, datasets, and results.
* **🔗 Interactive Citation Mapping:** Implement a feature to highlight the exact coordinates (page and paragraph) in the PDF source for every claim made by the LLM.
* **🧠 Knowledge Graph Integration:** Visualize the relationship between key concepts in the paper using a dynamic knowledge graph (e.g., using Pyvis or NetworkX).
* **🗂️ Persistent Session Management:** Integrate a lightweight database (like Supabase or SQLite) to allow users to save their research history and previous Q&A sessions.
* **✍️ Automated Study Notes:** Add an "Export to Markdown/Notion" feature to instantly turn a simplified paper into structured study notes or a journal entry.

---

## 👩‍💻 Author

**Akarshana Singh** *Data Scientist & Generative AI Developer*

⭐ **If you find this project useful, please consider giving it a star on GitHub!**