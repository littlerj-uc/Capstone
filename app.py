import streamlit as st
import anthropic
import re

# ── API Key Safety ────────────────────────────────────────────────
if "ANTHROPIC_API_KEY" not in st.secrets:
    st.error("Missing API key. Please configure Streamlit secrets.")
    st.stop()

client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

# ── Page config ───────────────────────────────────────────────────
st.set_page_config(
    page_title="ProcessPilot · Process Documentation Bot",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── (ALL YOUR CSS REMAINS EXACTLY THE SAME — OMITTED HERE FOR BREVITY) ──
# ⚠️ KEEP YOUR EXISTING CSS BLOCK UNCHANGED

# ── System prompt ─────────────────────────────────────────────────
SYSTEM_PROMPT = """You are ProcessPilot...
"""  # keep yours exactly

# ── Session state init ────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []

if "loading" not in st.session_state:
    st.session_state.loading = False

# 🧠 Guided mode state
if "chat_step" not in st.session_state:
    st.session_state.chat_step = 0

if "chat_data" not in st.session_state:
    st.session_state.chat_data = {
        "raw_input": "",
        "start": "",
        "stop": "",
        "roles": "",
        "refined": ""
    }

# ── Helpers ──────────────────────────────────────────────────────

def call_claude(text: str) -> str:
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": text
            }
        ],
    )
    return message.content[0].text

def render_markdown_output(md: str):
    html = md
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)

    lines = html.split('\n')
    result_lines = []
    in_ol = False
    in_ul = False

    for line in lines:
        ol_match = re.match(r'^\d+\. (.+)', line)
        ul_match = re.match(r'^[-*] (.+)', line)

        if ol_match:
            if not in_ol:
                if in_ul:
                    result_lines.append('</ul>')
                    in_ul = False
                result_lines.append('<ol>')
                in_ol = True
            result_lines.append(f'<li>{ol_match.group(1)}</li>')
        elif ul_match:
            if not in_ul:
                if in_ol:
                    result_lines.append('</ol>')
                    in_ol = False
                result_lines.append('<ul>')
                in_ul = True
            result_lines.append(f'<li>{ul_match.group(1)}</li>')
        else:
            if in_ol:
                result_lines.append('</ol>')
                in_ol = False
            if in_ul:
                result_lines.append('</ul>')
                in_ul = False

            stripped = line.strip()
            if stripped and not stripped.startswith('<'):
                result_lines.append(f'<p>{stripped}</p>')
            else:
                result_lines.append(line)

    html = '\n'.join(result_lines)
    st.markdown(f'<div class="output-body">{html}</div>', unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-icon">⚙️</div>
  <div class="hero-text">
    <h1>Process<span>Pilot</span></h1>
    <p>Paste in a process description. Get back structured documentation, instantly.</p>
  </div>
</div>
""", unsafe_allow_html=True)

# 🧠 MODE TOGGLE
mode = st.toggle("🧠 Guided Mode (Chatbot)", value=False)

st.markdown(
    f"""
    <div class="section-label">
        {"🤖 Guided Chatbot Mode" if mode else "📝 Standard Input Mode"}
    </div>
    """,
    unsafe_allow_html=True
)

# ── Guided Mode ──────────────────────────────────────────────────
if mode:
    st.markdown('<div class="intro-card">🤖 Guided Process Builder</div>', unsafe_allow_html=True)

    step = st.session_state.chat_step
    st.progress((step + 1) / 4)

    if st.button("🔄 Reset Guided Flow"):
        st.session_state.chat_step = 0
        st.session_state.chat_data = {
            "raw_input": "",
            "start": "",
            "stop": "",
            "roles": "",
            "refined": ""
        }
        st.rerun()

    if step == 0:
        st.write("👋 Let’s build your process step-by-step.")
        if st.button("Start"):
            st.session_state.chat_step = 1
            st.rerun()

    elif step == 1:
        user_input = st.text_area("Describe the process")

        if st.button("Next"):
            if user_input.strip():
                st.session_state.chat_data["raw_input"] = user_input
                st.session_state.chat_step = 2
                st.rerun()

    elif step == 2:
        start = st.text_input("What starts the process?")
        stop = st.text_input("What ends the process?")
        roles = st.text_input("Who is involved?")

        if st.button("Generate Draft"):
            combined_prompt = f"""
Process Description:
{st.session_state.chat_data["raw_input"]}

Start: {start}
End: {stop}
Roles: {roles}
"""
            output = call_claude(combined_prompt)
            st.session_state.chat_data["refined"] = output
            st.session_state.chat_step = 3
            st.rerun()

    elif step == 3:
        st.markdown("### ✨ Draft Output")
        render_markdown_output(st.session_state.chat_data["refined"])

        feedback = st.text_input("Give feedback or type DONE")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Refine"):
                updated = call_claude(f"""
Improve this:

{st.session_state.chat_data["refined"]}

Feedback:
{feedback}
""")
                st.session_state.chat_data["refined"] = updated
                st.rerun()

        with col2:
            if st.button("Done"):
                st.session_state.history.insert(0, {
                    "input": st.session_state.chat_data["raw_input"],
                    "output": st.session_state.chat_data["refined"],
                })
                st.session_state.chat_step = 0
                st.rerun()

# ── STANDARD MODE (YOUR ORIGINAL APP) ─────────────────────────────
if not mode:
    st.markdown("### 📝 Describe your process")

    process_input = st.text_area(
        "Process description",
        height=180,
    )

    if st.button("⚡ Generate Process Documentation"):
        if process_input.strip():
            output = call_claude(process_input)

            st.session_state.history.insert(0, {
                "input": process_input,
                "output": output
            })

            render_markdown_output(output)

# ── History ──────────────────────────────────────────────────────
if st.session_state.history:
    st.markdown("## 🕘 History")

    for item in st.session_state.history:
        with st.expander(item["input"][:50]):
            st.markdown(item["output"])
 
 
