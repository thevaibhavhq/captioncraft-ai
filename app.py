import streamlit as st
import anthropic
from supabase import create_client, Client

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
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Syne:wght@700;800&display=swap');

  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0D0D0D;
    color: #F0EDE8;
  }

  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding: 1.5rem 1rem 4rem 1rem; max-width: 680px; margin: auto; }

  /* ── Hero ── */
  .hero { text-align: center; padding: 2.5rem 0 1.8rem 0; }
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
  .hero-sub { font-size: 0.95rem; color: #888; margin: 0; line-height: 1.5; }

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

  /* ── Input overrides ── */
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

  /* ── Buttons ── */
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
  .stButton > button[kind="primary"]:disabled {
    background: #2A2A2A !important;
    color: #666 !important;
    opacity: 1 !important;
  }

  .stButton > button[kind="secondary"] {
    width: 100%;
    background: #1A1A1A !important;
    color: #999 !important;
    border: 1px solid #2E2E2E !important;
    border-radius: 10px !important;
    font-size: 0.85rem !important;
  }

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

  /* ── Usage badge ── */
  .usage-badge {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #161616;
    border: 1px solid #2A2A2A;
    border-radius: 12px;
    padding: 0.7rem 1rem;
    margin-bottom: 1rem;
    font-size: 0.82rem;
    color: #AAA;
  }
  .usage-badge strong { color: #C084FC; }

  /* ── Recharge card ── */
  .recharge-card {
    background: linear-gradient(135deg, #2A1F3D, #1A1326);
    border: 1px solid #7B5EA7;
    border-radius: 16px;
    padding: 1.6rem 1.4rem;
    text-align: center;
    margin: 1rem 0;
  }
  .recharge-card h3 {
    font-family: 'Syne', sans-serif;
    font-size: 1.3rem;
    color: #fff;
    margin: 0.4rem 0 0.5rem 0;
  }
  .recharge-card p {
    color: #BBB;
    font-size: 0.9rem;
    margin: 0 0 1rem 0;
    line-height: 1.5;
  }
  .recharge-icon { font-size: 2.2rem; }

  hr { border-color: #2A2A2A; margin: 1.4rem 0; }
  .tip-text { font-size: 0.78rem; color: #666; margin-top: 0.3rem; }
  .stAlert { border-radius: 10px !important; }

  /* ── Auth toggle ── */
  .auth-toggle-text { text-align: center; color: #888; font-size: 0.88rem; margin-top: 0.8rem; }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
PLATFORMS = ["Instagram", "LinkedIn", "Twitter/X", "YouTube", "Facebook", "TikTok"]
TONES = ["Professional", "Casual & Fun", "Inspirational", "Witty & Humorous", "Educational", "Storytelling"]
CAPTION_COUNTS = [1, 2, 3]

# 🔧 Update this with your real Razorpay payment link
RECHARGE_LINK = "https://razorpay.me/@yourbusiness"

PLATFORM_HINTS = {
    "Instagram":  "visual storytelling, hashtags, emojis, 150–220 chars ideal",
    "LinkedIn":   "professional value, hook opening, no excessive hashtags",
    "Twitter/X":  "punchy, under 280 chars, optional thread opener",
    "YouTube":    "SEO-friendly description opener, timestamps optional",
    "Facebook":   "conversational, question or CTA to drive comments",
    "TikTok":     "trendy, short hook, relevant hashtags, high energy",
}

# ── Supabase client ───────────────────────────────────────────────────────────
@st.cache_resource
def init_supabase() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_ANON_KEY"])

supabase = init_supabase()

# ── Auth helpers ──────────────────────────────────────────────────────────────
def sign_up(email, password):
    return supabase.auth.sign_up({"email": email, "password": password})

def sign_in(email, password):
    return supabase.auth.sign_in_with_password({"email": email, "password": password})

def get_profile(user_id):
    result = supabase.table("profiles").select("*").eq("id", user_id).execute()
    return result.data[0] if result.data else None

def deduct_credit(user_id, current_credits):
    new_credits = current_credits - 1
    supabase.table("profiles").update({"credits": new_credits}).eq("id", user_id).execute()
    return new_credits

# ── Session state init ────────────────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"  # "login" or "signup"

# ── AUTH PAGE ──────────────────────────────────────────────────────────────────
if not st.session_state.authenticated:
    st.markdown("""
    <div class="hero">
      <div class="hero-badge">✦ AI-Powered</div>
      <h1 class="hero-title">CaptionCraft AI</h1>
      <p class="hero-sub">Turn any idea into scroll-stopping social captions<br>in seconds. Powered by Claude.</p>
    </div>
    """, unsafe_allow_html=True)

    is_login = st.session_state.auth_mode == "login"
    title = "Sign In" if is_login else "Create Account"

    st.markdown(f'<div class="card"><div class="card-title">{title}</div>', unsafe_allow_html=True)

    email_input = st.text_input("Email", placeholder="you@email.com", key="auth_email")
    password_input = st.text_input("Password", type="password", placeholder="••••••••", key="auth_password")

    if is_login:
        action_clicked = st.button("✦ Sign In", type="primary", use_container_width=True)
    else:
        action_clicked = st.button("✦ Create Account", type="primary", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Toggle between login/signup
    if is_login:
        st.markdown('<p class="auth-toggle-text">New here?</p>', unsafe_allow_html=True)
        if st.button("Create an account", type="secondary", use_container_width=True):
            st.session_state.auth_mode = "signup"
            st.rerun()
    else:
        st.markdown('<p class="auth-toggle-text">Already have an account?</p>', unsafe_allow_html=True)
        if st.button("Sign in instead", type="secondary", use_container_width=True):
            st.session_state.auth_mode = "login"
            st.rerun()

    # ── Handle action ──
    if action_clicked:
        if not email_input.strip() or not password_input.strip():
            st.error("⚠️ Please enter both email and password.")
        elif len(password_input) < 6:
            st.error("⚠️ Password must be at least 6 characters.")
        else:
            try:
                if is_login:
                    res = sign_in(email_input.strip().lower(), password_input)
                    user = res.user
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user_id = user.id
                        st.session_state.user_email = user.email
                        st.rerun()
                    else:
                        st.error("⚠️ Invalid email or password.")
                else:
                    res = sign_up(email_input.strip().lower(), password_input)
                    if res.user:
                        st.success("✅ Account created! You can now sign in with your credentials. (Check your email if confirmation is enabled.)")
                        st.session_state.auth_mode = "login"
                    else:
                        st.error("⚠️ Could not create account. Try a different email.")
            except Exception as e:
                err_msg = str(e)
                if "already registered" in err_msg.lower() or "already exists" in err_msg.lower():
                    st.error("⚠️ This email is already registered. Try signing in instead.")
                elif "invalid login credentials" in err_msg.lower():
                    st.error("⚠️ Invalid email or password.")
                else:
                    st.error(f"⚠️ Authentication error: {err_msg}")

    st.stop()

# ── MAIN APP (authenticated users only) ───────────────────────────────────────
user_id = st.session_state.user_id
user_email = st.session_state.user_email

profile = get_profile(user_id)

if profile is None:
    st.error("⚠️ Could not load your profile. Please sign out and sign in again.")
    if st.button("Sign out", type="secondary", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.user_email = None
        supabase.auth.sign_out()
        st.rerun()
    st.stop()

credits = profile.get("credits", 0)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-badge">✦ AI-Powered</div>
  <h1 class="hero-title">CaptionCraft AI</h1>
  <p class="hero-sub">Turn any idea into scroll-stopping social captions<br>in seconds. Powered by Claude.</p>
</div>
""", unsafe_allow_html=True)

# ── Usage badge + logout ───────────────────────────────────────────────────────
st.markdown(f"""
<div class="usage-badge">
  <span>Signed in as <strong>{user_email}</strong></span>
  <span><strong>{credits}</strong> credits remaining</span>
</div>
""", unsafe_allow_html=True)

if st.button("Sign out", type="secondary", use_container_width=True):
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.user_email = None
    supabase.auth.sign_out()
    st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ── RECHARGE CARD (shown when out of credits) ──────────────────────────────────
if credits <= 0:
    st.markdown(f"""
    <div class="recharge-card">
      <div class="recharge-icon">⚡</div>
      <h3>You're out of credits</h3>
      <p>You've used all your generation credits. Recharge now to keep creating
      scroll-stopping captions for your content.</p>
    </div>
    """, unsafe_allow_html=True)

    st.link_button("✦ Recharge Credits", RECHARGE_LINK, type="primary", use_container_width=True)
    st.markdown('<p class="tip-text" style="text-align:center;">After payment, your credits will be updated automatically within a few minutes.</p>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

# ── Content Input ──────────────────────────────────────────────────────────────
st.markdown('<div class="card"><div class="card-title">Your Content</div>', unsafe_allow_html=True)

topic = st.text_area(
    "What's this post about?",
    placeholder="e.g. Launched my SaaS product after 3 months of solo building. It helps freelancers automate client invoicing.",
    height=110,
    disabled=(credits <= 0),
)

col1, col2 = st.columns(2)
with col1:
    platform = st.selectbox("Platform", PLATFORMS, disabled=(credits <= 0))
with col2:
    tone = st.selectbox("Tone", TONES, disabled=(credits <= 0))

keywords = st.text_input("Keywords / hashtags to include (optional)", placeholder="e.g. SaaS, entrepreneurship, buildinpublic", disabled=(credits <= 0))
num_captions = st.selectbox("How many captions?", CAPTION_COUNTS, index=1, disabled=(credits <= 0))

st.markdown('</div>', unsafe_allow_html=True)

# ── Advanced options ──────────────────────────────────────────────────────────
with st.expander("⚙️ Advanced options"):
    include_cta = st.toggle("Add a Call-To-Action (CTA)", value=True, disabled=(credits <= 0))
    include_hashtags = st.toggle("Include hashtag block", value=True, disabled=(credits <= 0))
    include_emoji = st.toggle("Use emojis", value=True, disabled=(credits <= 0))
    custom_instruction = st.text_input("Extra instruction (optional)", placeholder="e.g. Mention our launch discount ends Sunday", disabled=(credits <= 0))

# ── Generate ──────────────────────────────────────────────────────────────────
generate_clicked = st.button(
    "✦ Generate Captions",
    type="primary",
    use_container_width=True,
    disabled=(credits <= 0),
)

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

# ── API call helper ───────────────────────────────────────────────────────────
def call_claude(prompt):
    api_key = st.secrets["ANTHROPIC_API_KEY"]
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

def parse_captions(raw_text, num_captions):
    """Split raw output into individual captions."""
    captions = []
    if "---CAPTION" in raw_text:
        parts = raw_text.split("---CAPTION")
        for part in parts[1:]:
            lines = part.strip().splitlines()
            body_lines = [l for l in lines if not l.strip().startswith(("1", "2", "3")) or len(l.strip()) > 3]
            body = "\n".join(body_lines).strip().lstrip("---").strip()
            if body:
                captions.append(body)
    else:
        captions = [raw_text.strip()]
    return captions[:num_captions] if captions else [raw_text.strip()]

# ── Main logic ────────────────────────────────────────────────────────────────
if generate_clicked and credits > 0:
    if not topic.strip():
        st.error("⚠️ Tell us what your post is about.")
    elif "ANTHROPIC_API_KEY" not in st.secrets:
        st.error("⚠️ Service temporarily unavailable. (Admin: ANTHROPIC_API_KEY missing from Streamlit Secrets.)")
    else:
        prompt = build_prompt(
            topic, platform, tone, keywords, num_captions,
            include_cta, include_hashtags, include_emoji, custom_instruction
        )

        with st.spinner("Crafting your captions…"):
            try:
                raw = call_claude(prompt)
                captions = parse_captions(raw, num_captions)

                # Only deduct credit on a successful generation
                new_credits = deduct_credit(user_id, credits)

                st.markdown("---")
                st.markdown(f"**✦ {len(captions)} caption(s) for {platform} · {tone} tone**")

                for i, caption in enumerate(captions, 1):
                    st.markdown(f'<div class="caption-number">Caption {i} of {len(captions)}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="caption-box">{caption}</div>', unsafe_allow_html=True)
                    st.code(caption, language=None)   # one-tap copy on mobile
                    if i < len(captions):
                        st.markdown("<br>", unsafe_allow_html=True)

                st.success(f"Tap the copy icon on any code block to copy a caption. ({new_credits} credits remaining)")

                if new_credits <= 0:
                    st.info("⚡ That was your last credit. Refresh the page to see the recharge option.")

            except anthropic.AuthenticationError:
                st.error("⚠️ Service temporarily unavailable. (Admin: API key invalid — check Streamlit Secrets.)")
            except anthropic.APIError:
                st.error("⚠️ Our AI provider is having issues right now. Please try again shortly.")
            except Exception:
                st.error("⚠️ Something went wrong. Please try again. (Your credit was not deducted.)")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<hr>
<p style='text-align:center; color:#444; font-size:0.78rem;'>
  CaptionCraft AI · Built with Streamlit
</p>
""", unsafe_allow_html=True)
                    
