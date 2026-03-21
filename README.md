#🧠 AI Research Paper Simplifier

An AI-powered application that simplifies research papers using Retrieval-Augmented Generation (RAG).
Search for papers from arXiv, process them, and ask questions in natural language.

🔗 Live App: https://ai-research-paper-simplifier-ebbboh8duex77qdjzrwgyw.streamlit.app/


🚀 Features
🔍 Search research papers using arXiv API
📄 Extract and process PDF content
✂️ Intelligent text chunking with overlap
🧠 Semantic search using OpenAI embeddings
💬 Ask questions about the paper (RAG pipeline)
📚 Source-backed answers
🎯 Multiple explanation modes (Simple, Normal, Technical)
🎨 Clean and modern Streamlit UI
🧠 How It Works (RAG Pipeline)
Fetch paper using arXiv API
Download and extract PDF text (PyMuPDF)
Chunk text into overlapping segments
Generate embeddings using OpenAI
Retrieve relevant chunks using cosine similarity
Generate answers using LLM with retrieved context

🏗️ Architecture
User Query
   ↓
Embedding + Similarity Search
   ↓
Top Relevant Chunks
   ↓
Prompt Augmentation
   ↓
OpenAI LLM
   ↓
Final Answer + Sources

🛠️ Tech Stack
Frontend: Streamlit
LLM: OpenAI API
Embeddings: OpenAI Embeddings
Vector Search: Cosine Similarity
PDF Processing: PyMuPDF

⚙️ Installation
git clone https://github.com/your-username/ai-research-paper-simplifier.git
cd ai-research-paper-simplifier
pip install -r requirements.txt

🔐 Environment Variables

Create a .env file:

OPENAI_API_KEY=your_api_key_here


▶️ Run Locally
streamlit run app.py

📸 Screenshots


💥 Challenges & Solutions
❌ FAISS Dependency Issues

Faced compatibility problems while deploying FAISS on Streamlit Cloud.
Solution: Replaced FAISS with cosine similarity for lightweight and stable retrieval.

❌ Embedding Pipeline Inconsistency

Initial mismatch between embedding and retrieval logic.
Solution: Standardized pipeline using OpenAI embeddings for both indexing and querying.

❌ LLM Integration Errors

Issues with API usage and client initialization.
Solution: Refactored code to centralize OpenAI client usage inside modules.

❌ Deployment Errors (403 / Internal Server Error)

Faced authentication and runtime errors during deployment.
Solution: Used Streamlit Secrets for secure API key handling and fixed dependency issues.

❌ UI Styling Issues

Default Streamlit UI looked basic and inconsistent.
Solution: Implemented custom CSS for glassmorphism, layout balance, and improved UX.

❌ Input & Layout Bugs

Input fields appeared as white boxes breaking the theme.
Solution: Overrode Streamlit component styles using targeted CSS selectors.


🚀 Future Improvements
📊 Compare multiple research papers
🔗 Highlight citations directly in answers
🧠 Multi-document querying
🗂️ Save conversation history
📌 Key Learnings
Built an end-to-end RAG pipeline from scratch
Solved real-world deployment challenges
Improved understanding of LLM + retrieval integration
Gained experience in UI/UX for AI applications
👩‍💻 Author

Akarshana Singh

⭐ If you like this project

Give it a ⭐ on GitHub!

