import streamlit as st
import anthropic
import openai
import json

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CaptionCraft AI",
    page_icon="✦",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Import fonts */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Syne:wght@700;800&display=swap');

  /* Reset & base */
  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0D0D0D;
    color: #F0EDE8;
  }

  /* Hide Streamlit chrome */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding: 1.5rem 1rem 4rem 1rem; max-width: 680px; margin: auto; }

  /* ── Hero ── */
  .hero {
    text-align: center;
    padding: 2.5rem 0 1.8rem 0;
  }
  .hero-badge {
    display: inline-block;
    background: linear-gradient(135deg, #7B5EA7, #C084FC);
    color: #fff;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0.3rem 0.85rem;
    border-radius: 20px;
    margin-bottom: 1rem;
  }
  .hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2rem, 8vw, 2.8rem);
    font-weight: 800;
    line-height: 1.1;
    letter-spacing: -0.02em;
    margin: 0 0 0.6rem 0;
    background: linear-gradient(135deg, #F0EDE8 40%, #C084FC 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .hero-sub {
    font-size: 0.95rem;
    color: #888;
    margin: 0;
    line-height: 1.5;
  }

  /* ── Cards ── */
  .card {
    background: #161616;
    border: 1px solid #2A2A2A;
    border-radius: 16px;
    padding: 1.4rem 1.2rem;
    margin-bottom: 1rem;
  }
  .card-title {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #C084FC;
    margin-bottom: 0.8rem;
  }

  /* ── Streamlit input overrides ── */
  .stTextInput > div > div > input,
  .stTextArea > div > div > textarea,
  .stSelectbox > div > div {
    background-color: #1E1E1E !important;
    border: 1px solid #2E2E2E !important;
    border-radius: 10px !important;
    color: #F0EDE8 !important;
    font-size: 0.95rem !important;
  }
  .stTextInput > div > div > input:focus,
  .stTextArea > div > div > textarea:focus {
    border-color: #7B5EA7 !important;
    box-shadow: 0 0 0 2px rgba(123,94,167,0.25) !important;
  }
  label, .stSelectbox label, .stTextInput label, .stTextArea label {
    color: #AAA !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
  }

  /* ── Pills for platform / tone ── */
  div[data-testid="stHorizontalBlock"] .stButton > button {
    border-radius: 20px;
    border: 1px solid #2E2E2E;
    background: #1A1A1A;
    color: #AAA;
    font-size: 0.8rem;
    padding: 0.25rem 0.85rem;
    transition: all 0.15s ease;
  }
  div[data-testid="stHorizontalBlock"] .stButton > button:hover {
    border-color: #7B5EA7;
    color: #C084FC;
    background: #1E1628;
  }

  /* ── Generate button ── */
  .stButton > button[kind="primary"] {
    width: 100%;
    background: linear-gradient(135deg, #7B5EA7, #C084FC) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 0.75rem 1rem !important;
    letter-spacing: 0.02em;
    transition: opacity 0.2s ease;
  }
  .stButton > button[kind="primary"]:hover { opacity: 0.88; }

  /* ── Output caption box ── */
  .caption-box {
    background: #111;
    border: 1px solid #7B5EA7;
    border-radius: 14px;
    padding: 1.2rem 1.1rem;
    margin-top: 0.6rem;
    white-space: pre-wrap;
    font-size: 0.95rem;
    line-height: 1.65;
    color: #F0EDE8;
  }
  .caption-number {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #C084FC;
    margin-bottom: 0.4rem;
  }

  /* ── Divider ── */
  hr { border-color: #2A2A2A; margin: 1.4rem 0; }

  /* ── Misc ── */
  .tip-text { font-size: 0.78rem; color: #666; margin-top: 0.3rem; }
  .stAlert { border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
PLATFORMS = ["Instagram", "LinkedIn", "Twitter/X", "YouTube", "Facebook", "TikTok"]
TONES = ["Professional", "Casual & Fun", "Inspirational", "Witty & Humorous", "Educational", "Storytelling"]
CAPTION_COUNTS = [1, 2, 3]

PLATFORM_HINTS = {
    "Instagram":  "visual storytelling, hashtags, emojis, 150–220 chars ideal",
    "LinkedIn":   "professional value, hook opening, no excessive hashtags",
    "Twitter/X":  "punchy, under 280 chars, optional thread opener",
    "YouTube":    "SEO-friendly description opener, timestamps optional",
    "Facebook":   "conversational, question or CTA to drive comments",
    "TikTok":     "trendy, short hook, relevant hashtags, high energy",
}

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-badge">✦ AI-Powered</div>
  <h1 class="hero-title">CaptionCraft AI</h1>
  <p class="hero-sub">Turn any idea into scroll-stopping social captions<br>in seconds. Powered by Claude & GPT-4.</p>
</div>
""", unsafe_allow_html=True)

# ── Step 1: API Key ───────────────────────────────────────────────────────────
st.markdown('<div class="card"><div class="card-title">① API Key</div>', unsafe_allow_html=True)

provider = st.selectbox("AI Provider", ["Anthropic (Claude)", "OpenAI (GPT-4o)"], label_visibility="collapsed")
api_key = st.text_input(
    "API Key",
    type="password",
    placeholder="sk-ant-...  or  sk-...",
    label_visibility="collapsed",
)
st.markdown('<p class="tip-text">🔒 Your key is never stored. It lives only in this session.</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Step 2: Content Input ─────────────────────────────────────────────────────
st.markdown('<div class="card"><div class="card-title">② Your Content</div>', unsafe_allow_html=True)

topic = st.text_area(
    "What's this post about?",
    placeholder="e.g. Launched my SaaS product after 3 months of solo building. It helps freelancers automate client invoicing.",
    height=110,
)

col1, col2 = st.columns(2)
with col1:
    platform = st.selectbox("Platform", PLATFORMS)
with col2:
    tone = st.selectbox("Tone", TONES)

keywords = st.text_input("Keywords / hashtags to include (optional)", placeholder="e.g. SaaS, entrepreneurship, buildinpublic")
num_captions = st.selectbox("How many captions?", CAPTION_COUNTS, index=1)

st.markdown('</div>', unsafe_allow_html=True)

# ── Step 3: Advanced options (collapsed) ──────────────────────────────────────
with st.expander("⚙️ Advanced options"):
    include_cta = st.toggle("Add a Call-To-Action (CTA)", value=True)
    include_hashtags = st.toggle("Include hashtag block", value=True)
    include_emoji = st.toggle("Use emojis", value=True)
    custom_instruction = st.text_input("Extra instruction (optional)", placeholder="e.g. Mention our launch discount ends Sunday")

# ── Generate ──────────────────────────────────────────────────────────────────
generate_clicked = st.button("✦ Generate Captions", type="primary", use_container_width=True)

# ── Prompt builder ────────────────────────────────────────────────────────────
def build_prompt(topic, platform, tone, keywords, num_captions,
                 include_cta, include_hashtags, include_emoji, custom_instruction):
    hint = PLATFORM_HINTS.get(platform, "")
    kw_line = f"- Keywords/hashtags to work in: {keywords}" if keywords.strip() else ""
    cta_line = "- End each caption with a clear, natural Call-To-Action." if include_cta else "- Do NOT include a CTA."
    hashtag_line = "- Add a curated hashtag block (5–10 hashtags) at the end of each caption." if include_hashtags else "- Do NOT add hashtags."
    emoji_line = "- Use emojis to add personality and improve readability." if include_emoji else "- Do NOT use any emojis."
    custom_line = f"- Additional instruction: {custom_instruction}" if custom_instruction.strip() else ""

    prompt = f"""You are an expert social media copywriter. Generate {num_captions} distinct, high-performing caption(s) for {platform}.

Platform context: {hint}

POST DETAILS:
{topic}

REQUIREMENTS:
- Tone: {tone}
{kw_line}
{cta_line}
{hashtag_line}
{emoji_line}
{custom_line}

FORMAT:
Return exactly {num_captions} caption(s), each clearly separated by:
---CAPTION [N]---
(where N is the caption number)

Make each caption feel original and native to {platform}. Do not add any explanation outside the captions."""
    return prompt

# ── API call helpers ──────────────────────────────────────────────────────────
def call_claude(api_key, prompt):
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

def call_openai(api_key, prompt):
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
        temperature=0.85,
    )
    return response.choices[0].message.content

def parse_captions(raw_text, num_captions):
    """Split raw output into individual captions."""
    captions = []
    if "---CAPTION" in raw_text:
        parts = raw_text.split("---CAPTION")
        for part in parts[1:]:
            lines = part.strip().splitlines()
            # Remove the header line like "1---" or "[1]---"
            body_lines = [l for l in lines if not l.strip().startswith(("1", "2", "3")) or len(l.strip()) > 3]
            body = "\n".join(body_lines).strip().lstrip("---").strip()
            if body:
                captions.append(body)
    else:
        # Fallback: return as single caption
        captions = [raw_text.strip()]
    return captions[:num_captions] if captions else [raw_text.strip()]

# ── Main logic ────────────────────────────────────────────────────────────────
if generate_clicked:
    if not api_key.strip():
        st.error("⚠️ Please enter your API key above.")
    elif not topic.strip():
        st.error("⚠️ Tell us what your post is about.")
    else:
        prompt = build_prompt(
            topic, platform, tone, keywords, num_captions,
            include_cta, include_hashtags, include_emoji, custom_instruction
        )

        with st.spinner("Crafting your captions…"):
            try:
                if "Anthropic" in provider:
                    raw = call_claude(api_key, prompt)
                else:
                    raw = call_openai(api_key, prompt)

                captions = parse_captions(raw, num_captions)

                st.markdown("---")
                st.markdown(f"**✦ {len(captions)} caption(s) for {platform} · {tone} tone**")

                for i, caption in enumerate(captions, 1):
                    st.markdown(f'<div class="caption-number">Caption {i} of {len(captions)}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="caption-box">{caption}</div>', unsafe_allow_html=True)
                    st.code(caption, language=None)   # one-tap copy on mobile
                    if i < len(captions):
                        st.markdown("<br>", unsafe_allow_html=True)

                st.success("Tap the copy icon on any code block to copy a caption instantly.")

            except anthropic.AuthenticationError:
                st.error("Invalid Anthropic API key. Check and try again.")
            except openai.AuthenticationError:
                st.error("Invalid OpenAI API key. Check and try again.")
            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<hr>
<p style='text-align:center; color:#444; font-size:0.78rem;'>
  CaptionCraft AI · Built with Streamlit · Your key is never stored
</p>
""", unsafe_allow_html=True)
