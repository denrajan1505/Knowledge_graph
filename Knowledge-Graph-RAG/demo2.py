"""
app.py — Knowledge Graph Finance AI
Fully auto-initializes. No Load AI button. Voice search included.
"""
import os
import asyncio
import time
from dotenv import load_dotenv
import streamlit as st

from traditional_rag import TraditionalRAG
from knowledge_graph import KnowledgeGraphRAG

load_dotenv()

st.set_page_config(page_title="Knowledge Graph AI", page_icon="🤖", layout="wide")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
html,body,[class*="css"]{font-family:'Segoe UI',sans-serif;}
.stApp{background:linear-gradient(135deg,#141e30,#243b55);color:white;}

.main-title{
    text-align:center;font-size:48px;font-weight:800;
    background:linear-gradient(90deg,#00ffd5,#00ff87);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
    margin-bottom:4px;
}
.sub-title{text-align:center;color:#d7d7d7;margin-bottom:28px;font-size:16px;}

div.stButton>button{
    background:linear-gradient(90deg,#ffffff,#d9faff);
    color:#111!important;font-weight:700;border:none;
    border-radius:14px;padding:12px 10px;width:100%;min-height:56px;
    white-space:normal!important;line-height:1.4;transition:0.25s ease;
    font-size:13px;
}
div.stButton>button:hover{transform:scale(1.03);box-shadow:0 4px 16px rgba(0,255,213,0.25);}

.user-box{
    background:linear-gradient(135deg,#00c6ff,#0072ff);
    padding:14px 18px;border-radius:18px;margin:8px 0;color:white;
    font-size:15px;line-height:1.5;
}
.bot-box{
    background:linear-gradient(135deg,#d4fc79,#96e6a1);
    color:#111;padding:14px 18px;border-radius:18px;margin:8px 0;
    font-size:15px;line-height:1.5;
}
.cypher-box{
    background:#0d1117;color:#00ffd5;
    padding:14px;border-radius:10px;font-family:'Courier New',monospace;font-size:13px;
    white-space:pre-wrap;word-break:break-word;border:1px solid #00ffd533;
}

.typing{display:flex;gap:6px;padding:10px;}
.typing span{
    width:10px;height:10px;background:white;
    border-radius:50%;animation:bounce 1s infinite;
}
.typing span:nth-child(2){animation-delay:.2s;}
.typing span:nth-child(3){animation-delay:.4s;}
@keyframes bounce{0%,80%,100%{transform:scale(0);}40%{transform:scale(1);}}

.bulb-icon{font-size:26px;}
.section-title{font-size:22px;font-weight:700;margin:20px 0 12px 0;color:#fff;}

/* Voice */
.voice-wrap{text-align:center;padding:4px 0;}
#voice-btn{
    background:linear-gradient(135deg,#00ffd5,#00bfff);
    border:none;border-radius:50%;width:52px;height:52px;
    font-size:24px;cursor:pointer;box-shadow:0 0 14px #00ffd566;
    transition:.25s ease;display:inline-block;
}
#voice-btn:hover{transform:scale(1.12);}
#voice-btn.listening{
    animation:pulseRing 1s infinite;
    background:linear-gradient(135deg,#ff416c,#ff4b2b);
    box-shadow:0 0 22px #ff416c99;
}
@keyframes pulseRing{
    0%{box-shadow:0 0 0 0 rgba(255,65,108,.7);}
    70%{box-shadow:0 0 0 16px rgba(255,65,108,0);}
    100%{box-shadow:0 0 0 0 rgba(255,65,108,0);}
}
#voice-status{font-size:12px;color:#aef;min-height:18px;margin:5px 0 3px;}
#voice-transcript{
    background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.2);
    border-radius:8px;padding:7px 10px;font-size:13px;color:#e0ffe0;
    min-height:32px;margin-bottom:5px;word-break:break-word;display:none;
}
#voice-send-btn{
    background:linear-gradient(90deg,#00ff87,#00ffd5);color:#111;
    font-weight:700;border:none;border-radius:8px;padding:7px 18px;
    cursor:pointer;font-size:14px;width:100%;transition:.2s ease;display:none;
}
</style>
""", unsafe_allow_html=True)

# ── Voice JS ──────────────────────────────────────────────────────────────────
VOICE_JS = """
<div class="voice-wrap">
  <button id="voice-btn" title="Click to speak">🎤</button>
  <div id="voice-status">Click mic to speak</div>
  <div id="voice-transcript"></div>
  <button id="voice-send-btn" onclick="sendVoice()">➤ Send</button>
</div>
<script>
(function(){
  const btn=document.getElementById('voice-btn'),
        status=document.getElementById('voice-status'),
        trans=document.getElementById('voice-transcript'),
        sendB=document.getElementById('voice-send-btn'),
        SR=window.SpeechRecognition||window.webkitSpeechRecognition;

  if(!SR){status.textContent='⚠ Chrome only for Voice';btn.disabled=true;btn.style.opacity='.4';return;}

  const rec=new SR();
  rec.lang='en-IN'; rec.interimResults=true; rec.maxAlternatives=1;
  let listening=false, finalText='';

  btn.addEventListener('click',()=>listening?rec.stop():rec.start());

  rec.onstart=()=>{
    listening=true; btn.classList.add('listening');
    status.textContent='🔴 Listening…';
    finalText=''; trans.style.display='none'; sendB.style.display='none';
  };
  rec.onresult=(e)=>{
    let interim='';
    for(let i=e.resultIndex;i<e.results.length;i++)
      e.results[i].isFinal ? finalText+=e.results[i][0].transcript
                           : interim+=e.results[i][0].transcript;
    trans.style.display='block';
    trans.textContent=finalText||interim;
  };
  rec.onend=()=>{
    listening=false; btn.classList.remove('listening');
    finalText.trim() ? (status.textContent='✅ Click Send',sendB.style.display='block')
                     : (status.textContent='❌ Nothing heard');
  };
  rec.onerror=(e)=>{
    listening=false; btn.classList.remove('listening');
    status.textContent='⚠ '+e.error;
  };

  window.sendVoice=function(){
    const text=finalText.trim(); if(!text)return;
    const setter=Object.getOwnPropertyDescriptor(
      window.parent.HTMLTextAreaElement.prototype,'value').set;
    window.parent.document.querySelectorAll('textarea').forEach(el=>{
      setter.call(el,text);
      el.dispatchEvent(new Event('input',{bubbles:true}));
    });
    setTimeout(()=>{
      const ev=new KeyboardEvent('keydown',
        {key:'Enter',code:'Enter',keyCode:13,bubbles:true,cancelable:true});
      window.parent.document.querySelectorAll('textarea').forEach(el=>el.dispatchEvent(ev));
    },300);
    status.textContent='🚀 Sent!';
    trans.style.display='none'; sendB.style.display='none'; finalText='';
  };
})();
</script>
"""

# ── Session state ─────────────────────────────────────────────────────────────
DEFAULTS = {
    "messages":    [],
    "cypher_log":  {},
    "rag":         None,
    "kg":          None,
    "rag_ok":      False,
    "kg_ok":       False,
    "initialized": False,
    "init_errors": [],
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Auto-initialize (cached — runs ONCE per process) ──────────────────────────
@st.cache_resource(show_spinner=False)
def _init_systems():
    out = {"rag": None, "kg": None, "rag_ok": False, "kg_ok": False, "errors": []}

    # Traditional RAG
    try:
        rag = TraditionalRAG(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model_name="gpt-4",
            embedding_model="text-embedding-3-small",
        )
        docs = rag.load_documents("sample_data/personal_finance.txt")
        rag.build_index(docs)
        out["rag"] = rag
        out["rag_ok"] = True
    except Exception as e:
        out["errors"].append(f"Traditional RAG failed: {e}")

    # Knowledge Graph RAG
    try:
        kg = KnowledgeGraphRAG(
            neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            neo4j_user=os.getenv("NEO4J_USERNAME", "neo4j"),
            neo4j_password=os.getenv("NEO4J_PASSWORD", ""),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model_name="gpt-4",
        )
        out["kg"] = kg
        out["kg_ok"] = True
    except Exception as e:
        out["errors"].append(f"Knowledge Graph (Neo4j) failed: {e}")

    return out

# Run init once per session
if not st.session_state.initialized:
    with st.spinner("⚙️ Initializing AI systems…"):
        _s = _init_systems()
    st.session_state.rag         = _s["rag"]
    st.session_state.kg          = _s["kg"]
    st.session_state.rag_ok      = _s["rag_ok"]
    st.session_state.kg_ok       = _s["kg_ok"]
    st.session_state.init_errors = _s["errors"]
    st.session_state.initialized = True

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🤖 Knowledge Graph Finance AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Traditional RAG vs Knowledge Graph RAG · Dennis Rajan · March 2026</div>',
    unsafe_allow_html=True,
)

# Init error banner
for err in st.session_state.init_errors:
    st.error(err)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Control Panel")

    # Status
    st.markdown("**System Status**")
    st.markdown(f"{'🟢' if st.session_state.rag_ok else '🔴'} Traditional RAG")
    st.markdown(f"{'🟢' if st.session_state.kg_ok  else '🔴'} Knowledge Graph RAG")
    st.markdown("---")

    mode = st.selectbox(
        "Choose AI Mode",
        ["Traditional RAG", "Knowledge Graph RAG", "Compare Both"],
    )

    # Graph stats
    if st.session_state.kg_ok:
        try:
            stats = st.session_state.kg.get_graph_statistics()
            st.markdown(f"**📊 Graph:** {stats['total_nodes']} nodes · {stats['total_relationships']} edges")
        except Exception:
            pass

    st.markdown("---")
    if st.button("🧹 Clear Chat"):
        st.session_state.messages   = []
        st.session_state.cypher_log = {}
        st.rerun()

    st.markdown("---")
    st.markdown("### 🎙️ Voice Search")
    st.components.v1.html(VOICE_JS, height=160)

# ── Quick Questions ───────────────────────────────────────────────────────────
st.markdown(
    '<div class="section-title"><span class="bulb-icon">💡</span> Quick Questions</div>',
    unsafe_allow_html=True,
)

QUESTIONS = [
    "How much spent on food last month?",
    "What is the highest expense category?",
    "What are all EMI due dates?",
    "How much monthly income does Dennis have?",
    "Which loan has highest EMI?",
    "How much total shopping expense?",
    "What is current savings balance?",
    "Which credit card has highest bill?",
    "How much invested monthly?",
    "How much transport expense last month?",
    "What is bike EMI due date?",
    "How much overspending happened?",
]

cols = st.columns(3)
for i, q in enumerate(QUESTIONS):
    with cols[i % 3]:
        if st.button(q, key=f"qq_{i}"):
            st.session_state["_quick"] = q

# ── Chat history ──────────────────────────────────────────────────────────────
for idx, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        st.markdown(f'<div class="user-box">🧑&nbsp; {msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-box">🤖&nbsp; {msg["content"]}</div>', unsafe_allow_html=True)
        cypher = st.session_state.cypher_log.get(idx)
        if cypher:
            with st.expander("🔍 View Cypher Query"):
                st.markdown(f'<div class="cypher-box">{cypher}</div>', unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────────
prompt = st.chat_input("Ask anything about Dennis's finances… or use the 🎤 mic")

# Quick-question injection
if "_quick" in st.session_state:
    prompt = st.session_state.pop("_quick")

# ── Process ───────────────────────────────────────────────────────────────────
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    thinking = st.empty()
    thinking.markdown(
        '<div class="typing"><span></span><span></span><span></span></div>',
        unsafe_allow_html=True,
    )

    rag         = st.session_state.rag
    kg          = st.session_state.kg
    rag_ok      = st.session_state.rag_ok
    kg_ok       = st.session_state.kg_ok
    cypher_used = None

    def _offline():
        return (
            "⚠️ **Knowledge Graph RAG is offline.**\n\n"
            "Neo4j is unreachable. Ensure Neo4j is running on port 7687 "
            "and `.env` has `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`."
        )

    try:
        if mode == "Traditional RAG":
            if not rag_ok:
                response = "⚠️ Traditional RAG unavailable. Check your OpenAI API key."
            else:
                r = rag.query(prompt)
                response = r.get("answer", str(r)) if isinstance(r, dict) else str(r)

        elif mode == "Knowledge Graph RAG":
            if not kg_ok:
                response = _offline()
            else:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                r = loop.run_until_complete(kg.query(prompt))
                loop.close()
                response    = r.get("answer", str(r)) if isinstance(r, dict) else str(r)
                cypher_used = r.get("cypher") if isinstance(r, dict) else None

        else:  # Compare Both
            parts = []

            # Traditional RAG side
            if rag_ok:
                r = rag.query(prompt)
                rag_ans = r.get("answer", str(r)) if isinstance(r, dict) else str(r)
            else:
                rag_ans = "⚠️ Unavailable."
            parts.append(f"## 🔹 Traditional RAG\n\n{rag_ans}")

            # KG side
            if kg_ok:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                r = loop.run_until_complete(kg.query(prompt))
                loop.close()
                kg_ans      = r.get("answer", str(r)) if isinstance(r, dict) else str(r)
                cypher_used = r.get("cypher") if isinstance(r, dict) else None
            else:
                kg_ans = _offline()
            parts.append(f"---\n\n## 🔷 Knowledge Graph RAG\n\n{kg_ans}")

            response = "\n\n".join(parts)

    except Exception as e:
        response = f"⚠️ **Error:** {e}"

    time.sleep(0.6)
    thinking.empty()

    st.session_state.messages.append({"role": "assistant", "content": response})
    if cypher_used:
        st.session_state.cypher_log[len(st.session_state.messages) - 1] = cypher_used

    st.rerun()
