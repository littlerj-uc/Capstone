import streamlit as st
import anthropic
import re
client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
 
# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ProcessPilot · Process Documentation Bot",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)
 
# ── Inject custom CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');
 
  /* ── Root vars ── */
  :root {
    --bg:        #0F0F11;
    --bg2:       #17171B;
    --bg3:       #1E1E24;
    --border:    #2C2C36;
    --accent:    #C8F060;
    --accent2:   #60C8F0;
    --text:      #E8E8EE;
    --muted:     #7A7A8C;
    --danger:    #F06060;
    --radius:    12px;
  }
 
  /* ── Global reset ── */
  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background: var(--bg) !important;
    color: var(--text) !important;
  }
 
  /* ── Hide Streamlit chrome and remove reserved top space ── */
  #MainMenu, footer, header { display: none !important; }
  [data-testid="stHeader"],
  [data-testid="stToolbar"],
  [data-testid="stDecoration"] {
    display: none !important;
    height: 0 !important;
  }

  .stApp,
  [data-testid="stAppViewContainer"],
  [data-testid="stAppViewContainer"] > .main,
  [data-testid="stMain"],
  [data-testid="stMainBlockContainer"],
  .block-container {
    margin-top: 0 !important;
    padding-top: 0 !important;
  }

  [data-testid="stMainBlockContainer"],
  .block-container {
    max-width: 860px !important;
    margin-left: auto !important;
    margin-right: auto !important;
    padding-left: 24px !important;
    padding-right: 24px !important;
    padding-bottom: 80px !important;
  }
 
  /* ── Header ── */
  .hero {
    display: flex;
    align-items: flex-start;
    gap: 18px;
    padding-bottom: 24px;
    border-bottom: 1px solid var(--border);
  }
  .hero-icon {
    width: 52px; height: 52px;
    background: var(--accent);
    border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 26px;
    flex-shrink: 0;
    box-shadow: 0 0 28px rgba(200,240,96,.25);
  }
  .hero-text h1 {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    line-height: 1.1;
    margin: 0 0 6px;
    color: var(--text);
  }
  .hero-text h1 span { color: var(--accent); }
  .hero-text p {
    font-size: .95rem;
    color: var(--muted);
    margin: 0;
    line-height: 1.6;
  }
 
  /* ── Bot intro card ── */
  .intro-card {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: var(--radius);
    padding: 20px 24px;
    font-size: .95rem;
    line-height: 1.7;
    color: var(--text);
  }
  .intro-card strong { color: var(--accent); }
 
  /* ── Section label ── */
  .section-label {
    font-family: 'DM Mono', monospace;
    font-size: .7rem;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 8px;
  }
 
  /* ── Textarea ── */
  textarea {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: .95rem !important;
    resize: vertical !important;
    transition: border-color .2s !important;
  }
  textarea:focus { border-color: var(--accent) !important; outline: none !important; box-shadow: 0 0 0 3px rgba(200,240,96,.08) !important; }
 
  /* ── Primary button ── */
  div.stButton > button {
    background: var(--accent) !important;
    color: #0F0F11 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: .95rem !important;
    border: none !important;
    border-radius: var(--radius) !important;
    padding: 12px 28px !important;
    cursor: pointer !important;
    transition: opacity .15s, transform .1s !important;
    width: 100% !important;
  }
  div.stButton > button:hover { opacity: .88 !important; transform: translateY(-1px) !important; }
  div.stButton > button:active { transform: translateY(0) !important; }
  div.stButton > button:disabled { opacity: .4 !important; cursor: not-allowed !important; }
 
  /* ── Output container ── */
  .output-wrap {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
  }
  .output-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 20px;
    background: var(--bg3);
    border-bottom: 1px solid var(--border);
    font-family: 'DM Mono', monospace;
    font-size: .75rem;
    letter-spacing: .08em;
    color: var(--muted);
  }
  .output-header .badge {
    background: rgba(200,240,96,.12);
    color: var(--accent);
    border-radius: 20px;
    padding: 2px 10px;
    font-size: .7rem;
  }
  .output-body {
    padding: 24px;
  }
 
  /* ── Rendered markdown inside output ── */
  .output-body h2 {
    font-family: 'DM Serif Display', serif;
    font-size: 1.25rem;
    color: var(--accent2);
    margin: 24px 0 10px;
    border-bottom: 1px solid var(--border);
    padding-bottom: 6px;
  }
  .output-body h2:first-child { margin-top: 0; }
  .output-body h3 {
    font-size: 1rem;
    font-weight: 600;
    color: var(--accent);
    margin: 16px 0 6px;
  }
  .output-body p { margin: 0 0 10px; line-height: 1.7; }
  .output-body ol, .output-body ul {
    padding-left: 1.4em;
    margin: 0 0 12px;
    line-height: 1.8;
  }
  .output-body li { margin-bottom: 4px; }
  .output-body code {
    font-family: 'DM Mono', monospace;
    background: var(--bg3);
    border-radius: 4px;
    padding: 1px 6px;
    font-size: .85em;
    color: var(--accent);
  }
  .output-body blockquote {
    border-left: 3px solid var(--accent);
    margin: 12px 0;
    padding: 8px 16px;
    background: rgba(200,240,96,.05);
    border-radius: 0 8px 8px 0;
    color: var(--muted);
    font-style: italic;
  }
  .output-body strong { color: var(--text); font-weight: 600; }
 
  /* ── Spinner / thinking ── */
  .thinking {
    display: flex;
    align-items: center;
    gap: 10px;
    color: var(--muted);
    font-size: .9rem;
    padding: 16px 0;
  }
  .dot-pulse { display: flex; gap: 5px; }
  .dot-pulse span {
    width: 7px; height: 7px;
    background: var(--accent);
    border-radius: 50%;
    animation: pulse 1.2s ease-in-out infinite;
  }
  .dot-pulse span:nth-child(2) { animation-delay: .2s; }
  .dot-pulse span:nth-child(3) { animation-delay: .4s; }
  @keyframes pulse { 0%,80%,100%{opacity:.2;transform:scale(.8)} 40%{opacity:1;transform:scale(1)} }
 
  /* ── History items ── */
  .history-item {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px 20px;
    font-size: .875rem;
  }
  .history-item .hi-label {
    font-family: 'DM Mono', monospace;
    font-size: .65rem;
    letter-spacing: .1em;
    color: var(--muted);
    text-transform: uppercase;
    margin-bottom: 6px;
  }
  .history-item .hi-excerpt {
    color: var(--muted);
    line-height: 1.5;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
 
  /* ── Divider ── */
  hr { border: none; border-top: 1px solid var(--border); margin: 8px 0; }
 
  /* ── Coming soon pill ── */
  .coming-soon {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(96,200,240,.08);
    border: 1px solid rgba(96,200,240,.2);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: .75rem;
    color: var(--accent2);
    font-family: 'DM Mono', monospace;
    letter-spacing: .06em;
  }
 
  /* ── Streamlit element overrides ── */
  .stTextArea label { display: none !important; }
  div[data-testid="stVerticalBlock"] > div { padding: 0 !important; }
  .element-container { margin: 0 !important; }

  /* ── Mobile tweaks ── */
  @media (max-width: 768px) {
    [data-testid="stMainBlockContainer"],
    .block-container {
      padding-left: 14px !important;
      padding-right: 14px !important;
      padding-bottom: 48px !important;
    }

    .hero {
      gap: 12px;
      padding-bottom: 18px;
    }

    .hero-text h1 {
      font-size: 1.7rem;
    }

    .intro-card {
      padding: 16px 16px;
    }
  }
</style>
""", unsafe_allow_html=True)
 
 
# ── System prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are ProcessPilot, an expert business analyst and technical writer specializing in transforming raw process descriptions into clear, structured process documentation.
 
When given a process description, you produce a comprehensive, well-organized document using the following structure. Use markdown with ## for main sections and ### for subsections.
 
## Process Overview
A concise 2–3 sentence summary of the process, its purpose, and business value.
 
## Trigger
What initiates or kicks off this process.
 
## Roles & Responsibilities
A bulleted list of each role involved and their responsibility in this process.
 
## Prerequisites
What must be in place or true before the process can begin (systems, data, permissions, prior steps, etc.).
 
## Step-by-Step Instructions
Numbered steps written in clear, imperative language (e.g., "Click…", "Enter…", "Verify…"). Group related steps under ### sub-headings if the process has distinct phases. Each step should be specific and actionable.
 
## Exception Handling
A dedicated section listing potential exceptions, errors, or edge cases that may occur during the process. For each:
- **Exception**: Describe what can go wrong
- **Action**: What the responsible party should do
 
## Completion Criteria
How to determine the process has been completed successfully.
 
## Notes & Tips
Any important caveats, best practices, system-specific nuances, or tips that help the process run smoothly.
 
---
Rules:
- Be thorough but concise — no padding or filler
- Use plain, professional language — no jargon unless it was in the input
- If information for a section cannot be inferred from the input, write "To be defined — [brief explanation of what's needed]" rather than guessing
- Format must be clean markdown
"""
 
# ── Intro message ─────────────────────────────────────────────────────────────
INTRO_HTML = """
<div class="intro-card">
  👋 <strong>Hi, I'm ProcessPilot.</strong><br><br>
  I turn rough process descriptions into clean, structured documentation — complete with step-by-step instructions, role assignments, exception handling, and completion criteria.<br><br>
  <strong>To get started:</strong> paste or type a description of any business or technical process below. It can be a brain dump, bullet points, or a paragraph — I'll handle the structure.<br><br>
  <em style="color:#7A7A8C;">The more detail you provide, the richer the output. But even a rough description will give you a solid starting framework.</em>
</div>
"""
 
# ── Session state init ────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []   # list of {input, output}
if "loading" not in st.session_state:
    st.session_state.loading = False
 
 
# ── Helpers ───────────────────────────────────────────────────────────────────
def call_claude(process_text: str) -> str:
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": process_text}],
    )
    return message.content[0].text
 
 
def render_markdown_output(md: str):
    """Render markdown as styled HTML inside the output container."""
    # Convert markdown to basic HTML
    html = md
 
    # Headers
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
 
    # Bold
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
 
    # Italic
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
 
    # Code inline
    html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)
 
    # Horizontal rule
    html = re.sub(r'^---+$', r'<hr>', html, flags=re.MULTILINE)
 
    # Numbered lists
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
 
    if in_ol:
        result_lines.append('</ol>')
    if in_ul:
        result_lines.append('</ul>')
 
    html = '\n'.join(result_lines)
 
    st.markdown(f'<div class="output-body">{html}</div>', unsafe_allow_html=True)
 
 
# ── UI ────────────────────────────────────────────────────────────────────────
 
# Header
st.markdown("""
<div class="hero">
  <div class="hero-icon">⚙️</div>
  <div class="hero-text">
    <h1>Process<span>Pilot</span></h1>
    <p>Paste in a process description. Get back structured documentation, instantly.</p>
  </div>
</div>
""", unsafe_allow_html=True)
 
# Bot intro
st.markdown(INTRO_HTML, unsafe_allow_html=True)
 
# Divider
st.markdown("<hr>", unsafe_allow_html=True)
 
# Input section
st.markdown('<div class="section-label">📝 Describe your process</div>', unsafe_allow_html=True)
 
process_input = st.text_area(
  label="Process description",
  label_visibility="collapsed",
    placeholder="e.g. When a new employee joins the company, HR sends them a welcome email, IT sets up their laptop and accounts, their manager schedules a 1:1, and they complete compliance training within the first week...",
    height=180,
    key="process_input",
)
 
col1, col2 = st.columns([3, 1])
with col1:
    submit = st.button(
        "⚡ Generate Process Documentation",
        disabled=not process_input.strip() or st.session_state.loading,
        key="submit_btn",
    )
with col2:
    st.markdown("""
    <div style="padding-top:8px;">
      <span class="coming-soon">🔮 v2 features coming</span>
    </div>
    """, unsafe_allow_html=True)
 
# ── Handle submit ─────────────────────────────────────────────────────────────
if submit and process_input.strip():
    st.session_state.loading = True
    with st.spinner(""):
        st.markdown("""
        <div class="thinking">
          <div class="dot-pulse"><span></span><span></span><span></span></div>
          Analyzing process and generating documentation…
        </div>
        """, unsafe_allow_html=True)
        try:
            output = call_claude(process_input.strip())
            st.session_state.history.insert(0, {
                "input": process_input.strip(),
                "output": output,
            })
        except Exception as e:
            st.error(f"Something went wrong: {e}")
        finally:
            st.session_state.loading = False
    st.rerun()
 
# ── Show latest result ────────────────────────────────────────────────────────
if st.session_state.history:
    latest = st.session_state.history[0]
 
    st.markdown('<div class="section-label">📄 Generated Documentation</div>', unsafe_allow_html=True)
 
    st.markdown("""
    <div class="output-wrap">
      <div class="output-header">
        <span>PROCESS DOCUMENTATION</span>
        <span class="badge">✓ Generated</span>
      </div>
    """, unsafe_allow_html=True)
 
    render_markdown_output(latest["output"])
 
    st.markdown('</div>', unsafe_allow_html=True)
 
    # Copy raw button
    with st.expander("📋 View raw markdown"):
        st.code(latest["output"], language="markdown")
 
# ── History ───────────────────────────────────────────────────────────────────
if len(st.session_state.history) > 1:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">🕘 Previous Runs</div>', unsafe_allow_html=True)
 
    for i, item in enumerate(st.session_state.history[1:], 1):
        excerpt = item["input"][:120].replace("\n", " ")
        st.markdown(f"""
        <div class="history-item">
          <div class="hi-label">Run #{i}</div>
          <div class="hi-excerpt">{excerpt}{"…" if len(item["input"]) > 120 else ""}</div>
        </div>
        """, unsafe_allow_html=True)
 
        with st.expander(f"View output for run #{i}"):
            st.markdown(item["output"])
 
# ── Coming soon section ───────────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
<div style="display:flex; flex-direction:column; gap:10px;">
  <div class="section-label">🔮 Version 2 Roadmap</div>
  <div style="display:flex; flex-wrap:wrap; gap:10px; font-size:.85rem; color:#7A7A8C;">
    <div style="background:#17171B; border:1px solid #2C2C36; border-radius:8px; padding:10px 16px; flex:1; min-width:180px;">
      <div style="color:#60C8F0; font-weight:600; margin-bottom:4px;">🎙️ Voice / Transcript Input</div>
      Submit a voice recording or meeting transcript as your process source.
    </div>
    <div style="background:#17171B; border:1px solid #2C2C36; border-radius:8px; padding:10px 16px; flex:1; min-width:180px;">
      <div style="color:#60C8F0; font-weight:600; margin-bottom:4px;">✍️ Guided Input Mode</div>
      Answer structured questions: trigger, completion criteria, roles.
    </div>
    <div style="background:#17171B; border:1px solid #2C2C36; border-radius:8px; padding:10px 16px; flex:1; min-width:180px;">
      <div style="color:#60C8F0; font-weight:600; margin-bottom:4px;">🧹 Output Cleanup</div>
      Give feedback on the draft and iterate to a polished final version.
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

 
 
