# 🤖 Knowledge Graph Finance AI

A Streamlit app comparing **Traditional RAG** vs **Knowledge Graph RAG** for personal finance Q&A using Neo4j + GPT-4.

---

## 📁 Folder Structure

```
Knowledge-Graph-RAG/
│
├── demo2.py                          # ✅ Main Streamlit app (run this)
├── traditional_rag.py                # ✅ Traditional RAG implementation
├── comparison.py                     # ✅ Comparison utilities
├── requirements.txt                  # ✅ Python dependencies
├── .env.example                      # ✅ Environment variable template (NOT .env)
│
├── knowledge_graph/                  # ✅ Knowledge Graph package
│   ├── __init__.py                   # ✅ Exports KnowledgeGraphRAG
│   ├── kg_pipeline.py                # ✅ NEW - Main KG logic (Neo4j + GPT-4)
│   └── query.py                      # ✅ Query utilities
│
├── sample_data/                      # ✅ Finance data
│   └── personal_finance.txt          # ✅ Dennis Rajan finance profile
│
└── .gitignore                        # ✅ Ignore .env, venv, __pycache__
```

---

## ❌ Do NOT push these files

```
.env                        # Contains your secret API keys
venv/                       # Virtual environment (huge, not needed)
__pycache__/                # Python cache files
knowledge_graph/__pycache__/
*.pyc                       # Compiled Python files
debug_kg.py                 # Debug/temp scripts
fix_kg.py                   # One-time fix script
fix_import.py               # One-time fix script
check_file.py               # One-time fix script
knowledge_graph.py          # Root-level file (now replaced by kg_pipeline.py)
demo.py                     # Old demo file
demo1.py                    # Old demo file
comparison_metrics.png      # Generated output
knowledge_graph.html        # Generated output
```

---

## 🚀 Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/Knowledge-Graph-RAG.git
cd Knowledge-Graph-RAG
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup environment variables
```bash
copy .env.example .env       # Windows
cp .env.example .env         # Mac/Linux
```
Then edit `.env` and fill in your keys.

### 5. Start Neo4j
- Open **Neo4j Desktop**
- Start your database
- Make sure it's running on `bolt://localhost:7687`

### 6. Run the app
```bash
streamlit run demo2.py
```

---

## ⚙️ Environment Variables

Create a `.env` file with these values:

```env
OPENAI_API_KEY=your_openai_api_key_here
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password_here
```

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Streamlit | Frontend UI |
| Neo4j | Graph Database |
| OpenAI GPT-4 | LLM for Cypher generation + answers |
| LangChain | Traditional RAG pipeline |
| Python neo4j driver | Direct Neo4j connection |

---

## 💡 Features

- 🔹 **Traditional RAG** — Vector similarity search over finance documents
- 🔷 **Knowledge Graph RAG** — Structured Neo4j graph with GPT-4 Cypher generation
- ⚖️ **Compare Both** — Side-by-side answer comparison
- 🎤 **Voice Search** — Speak your question (Chrome/Edge)
- 🔍 **Cypher Viewer** — See the exact graph query used
