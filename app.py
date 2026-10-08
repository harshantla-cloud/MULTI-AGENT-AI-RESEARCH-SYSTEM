"""
Multi-Agent Research System — Streamlit UI

This file is intentionally kept as the frontend/orchestration layer.
The existing agents.py, tools.py and pipeline.py remain responsible for
the actual research logic.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import streamlit as st


# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Research Studio",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Project / environment setup
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

# Make local project imports reliable when Streamlit is launched from another
# working directory.
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


def load_streamlit_secrets_into_env() -> None:
    """
    Streamlit Cloud exposes secrets through st.secrets, while the existing
    project reads credentials with os.getenv()/python-dotenv.

    Copy only the keys this project actually uses into the environment so the
    existing backend can run without rewriting its credential logic.
    """
    for key in ("GOOGLE_API_KEY", "TAVILY_API_KEY"):
        try:
            value = st.secrets.get(key)
        except Exception:
            value = None

        if value:
            os.environ[key] = str(value)


load_streamlit_secrets_into_env()


# Import the existing backend only after credentials are prepared.
# This is important because tools.py validates TAVILY_API_KEY at import time
# and agents.py initializes the Gemini model at import time.
_BACKEND_IMPORT_ERROR = None

try:
    from pipeline import run_research_pipeline
except Exception as exc:
    run_research_pipeline = None
    _BACKEND_IMPORT_ERROR = exc


# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    /* ---------- Global ---------- */
    :root {
        --ink: #1f1f1d;
        --muted: #6b6b66;
        --soft: #f7f6f2;
        --line: #e8e6df;
        --card: #ffffff;
        --accent: #d97757;
    }

    .stApp {
        background:
            radial-gradient(circle at 80% 0%, rgba(217,119,87,0.06), transparent 28rem),
            #fbfaf7;
        color: var(--ink);
    }

    [data-testid="stHeader"] {
        background: rgba(251,250,247,0.78);
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2.6rem;
        padding-bottom: 5rem;
    }

    /* ---------- Sidebar ---------- */
    [data-testid="stSidebar"] {
        background: #f5f3ee;
        border-right: 1px solid var(--line);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
    }

    .brand {
        padding: 0.4rem 0.2rem 1.35rem;
    }

    .brand-mark {
        width: 38px;
        height: 38px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #242421;
        color: white;
        font-weight: 700;
        margin-bottom: 0.8rem;
        letter-spacing: -0.04em;
    }

    .brand-title {
        font-size: 1.05rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #20201d;
    }

    .brand-subtitle {
        color: var(--muted);
        font-size: 0.78rem;
        line-height: 1.45;
        margin-top: 0.25rem;
    }

    .side-card {
        border: 1px solid #e4e1d9;
        background: rgba(255,255,255,0.62);
        border-radius: 14px;
        padding: 0.9rem 0.9rem;
        margin: 0.75rem 0;
    }

    .side-label {
        color: #88877f;
        text-transform: uppercase;
        font-size: 0.64rem;
        letter-spacing: 0.09em;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }

    .side-value {
        color: #2a2a27;
        font-size: 0.82rem;
        line-height: 1.45;
    }

    /* ---------- Hero ---------- */
    .hero {
        padding: 0.5rem 0 1.8rem;
    }

    .eyebrow {
        color: #8a5b4a;
        text-transform: uppercase;
        letter-spacing: 0.13em;
        font-size: 0.68rem;
        font-weight: 800;
        margin-bottom: 0.65rem;
    }

    .hero h1 {
        font-size: clamp(2.25rem, 5vw, 4.15rem);
        line-height: 0.98;
        letter-spacing: -0.055em;
        margin: 0;
        max-width: 820px;
        color: #20201d;
        font-weight: 760;
    }

    .hero p {
        max-width: 720px;
        color: #6d6c66;
        font-size: 1.03rem;
        line-height: 1.65;
        margin-top: 1.1rem;
    }

    /* ---------- Cards ---------- */
    .section-card {
        background: rgba(255,255,255,0.84);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 1.25rem 1.35rem;
        box-shadow: 0 12px 36px rgba(30,30,25,0.035);
        margin-bottom: 1rem;
    }

    .section-title {
        font-size: 0.86rem;
        font-weight: 750;
        color: #353531;
        margin-bottom: 0.2rem;
    }

    .section-caption {
        color: #85837c;
        font-size: 0.76rem;
        line-height: 1.45;
        margin-bottom: 0.9rem;
    }

    .empty-state {
        border: 1px dashed #d9d6ce;
        border-radius: 18px;
        padding: 3rem 1.5rem;
        text-align: center;
        background: rgba(255,255,255,0.45);
    }

    .empty-title {
        color: #34342f;
        font-weight: 700;
        font-size: 1rem;
    }

    .empty-copy {
        color: #85837c;
        font-size: 0.84rem;
        max-width: 520px;
        margin: 0.45rem auto 0;
        line-height: 1.55;
    }

    .result-label {
        color: #8a5b4a;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-size: 0.65rem;
        font-weight: 800;
        margin-bottom: 0.45rem;
    }

    .source-chip {
        display: inline-block;
        padding: 0.38rem 0.62rem;
        border: 1px solid #e5e1d8;
        border-radius: 999px;
        background: #faf9f6;
        color: #5d5b55;
        font-size: 0.72rem;
        margin: 0.15rem 0.2rem 0.15rem 0;
    }

    /* ---------- Streamlit controls ---------- */
    textarea {
        border-radius: 14px !important;
    }

    div[data-testid="stTextArea"] textarea {
        background: #ffffff !important;
        border: 1px solid #ddd9d0 !important;
        color: #22221f !important;
        box-shadow: 0 5px 20px rgba(30,30,25,0.025);
    }

    div[data-testid="stButton"] > button {
        border-radius: 10px;
        min-height: 2.65rem;
        font-weight: 650;
        border: 1px solid #d9d6ce;
    }

    div[data-testid="stButton"] > button[kind="primary"] {
        background: #242421;
        border-color: #242421;
        color: white;
    }

    div[data-testid="stDownloadButton"] > button {
        border-radius: 10px;
        font-weight: 650;
    }

    /* Keep the default Streamlit menu/footer visually quiet. */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def extract_urls(text: str) -> list[str]:
    """Extract unique HTTP(S) URLs from the existing pipeline output."""
    if not text:
        return []

    found = re.findall(r"https?://[^\s<>\]\)\"']+", text)
    urls = []

    for url in found:
        url = url.rstrip(".,;:!?")
        if url not in urls:
            urls.append(url)

    return urls


def reset_research() -> None:
    """Clear the current research session."""
    for key in (
        "research_result",
        "research_topic",
        "research_error",
    ):
        st.session_state.pop(key, None)


def render_empty_state() -> None:
    st.markdown(
        """
        <div class="empty-state">
            <div class="empty-title">Your research workspace is ready</div>
            <div class="empty-copy">
                Enter a topic above to search multiple sources, extract
                evidence, generate a structured report, and review it with
                an independent critic agent.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-mark">R</div>
            <div class="brand-title">Research Studio</div>
            <div class="brand-subtitle">
                Multi-agent research workspace built around the existing
                research pipeline.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Clear current research", use_container_width=True):
        reset_research()
        st.rerun()

    st.markdown(
        """
        <div class="side-card">
            <div class="side-label">Architecture</div>
            <div class="side-value">
                Search Agent → Reader Agent → Writer → Critic
            </div>
        </div>

        <div class="side-card">
            <div class="side-label">AI model</div>
            <div class="side-value">Google Gemini 2.5 Flash</div>
        </div>

        <div class="side-card">
            <div class="side-label">Research tools</div>
            <div class="side-value">
                Tavily Search · Requests · BeautifulSoup · LangChain
            </div>
        </div>

        <div class="side-card">
            <div class="side-label">Output</div>
            <div class="side-value">
                Search evidence, multi-source research, final report and
                critic review.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.caption("Credentials are read from environment variables or Streamlit secrets.")


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Multi-agent research system</div>
        <h1>Turn a question into a researched report.</h1>
        <p>
            Give the system a research topic. The existing pipeline searches
            for relevant sources, reads selected pages, writes a structured
            report, and then critiques the result for quality and completeness.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

if _BACKEND_IMPORT_ERROR is not None:
    st.error(
        "The existing backend could not be loaded. Check the project dependencies "
        "and API credentials before running the app."
    )
    with st.expander("Technical details"):
        st.code(str(_BACKEND_IMPORT_ERROR))
    st.stop()


# Input card
st.markdown(
    """
    <div class="section-card">
        <div class="section-title">Research brief</div>
        <div class="section-caption">
            Use a focused topic or question. The existing multi-agent pipeline
            will decide which sources to research.
        </div>
    """,
    unsafe_allow_html=True,
)

topic = st.text_area(
    "Research topic",
    value=st.session_state.get("research_topic", ""),
    placeholder=(
        "Example: How is generative AI changing software development in 2026?"
    ),
    height=125,
    label_visibility="collapsed",
)

col1, col2 = st.columns([1, 5])

with col1:
    run_clicked = st.button(
        "Run research",
        type="primary",
        use_container_width=True,
    )

with col2:
    st.caption(
        "The existing backend may take some time because it performs live search, "
        "web scraping, generation and critique."
    )

st.markdown("</div>", unsafe_allow_html=True)


# Run pipeline
if run_clicked:
    cleaned_topic = topic.strip()

    if not cleaned_topic:
        st.warning("Enter a research topic before starting.")
    else:
        st.session_state["research_topic"] = cleaned_topic
        st.session_state.pop("research_error", None)

        with st.status(
            "Running the research pipeline…",
            expanded=True,
        ) as status:
            st.write("Searching for relevant sources…")
            st.write("Reading selected source pages…")
            st.write("Generating the research report…")
            st.write("Critiquing the report…")

            try:
                result = run_research_pipeline(cleaned_topic)
                st.session_state["research_result"] = result
                status.update(
                    label="Research completed",
                    state="complete",
                    expanded=False,
                )
            except Exception as exc:
                st.session_state["research_error"] = str(exc)
                status.update(
                    label="Research failed",
                    state="error",
                    expanded=True,
                )

        if st.session_state.get("research_error"):
            st.error(
                "The research run could not be completed. "
                "Check the API keys, network access and backend dependencies."
            )
            with st.expander("Technical details"):
                st.code(st.session_state["research_error"])


# Results
result = st.session_state.get("research_result")

if not result:
    render_empty_state()
    st.stop()


st.markdown(
    f"""
    <div class="section-card">
        <div class="result-label">Research topic</div>
        <div style="font-size:1.25rem;font-weight:700;letter-spacing:-0.02em;">
            {st.session_state.get("research_topic", "Research")}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# Final report is intentionally the primary visual output.
st.markdown(
    """
    <div class="section-card">
        <div class="section-title">Research report</div>
        <div class="section-caption">
            Generated by the existing Writer Chain using the gathered research.
        </div>
    """,
    unsafe_allow_html=True,
)

report = result.get("report", "")

if report:
    st.markdown(report)
else:
    st.info("No final report was returned by the existing pipeline.")

st.markdown("</div>", unsafe_allow_html=True)


# Critic review
st.markdown(
    """
    <div class="section-card">
        <div class="section-title">Critic review</div>
        <div class="section-caption">
            A separate critic chain reviews the generated report for factual
            quality, source usage, clarity and completeness.
        </div>
    """,
    unsafe_allow_html=True,
)

feedback = result.get("feedback", "")
if feedback:
    st.markdown(feedback)
else:
    st.info("No critic feedback was returned.")

st.markdown("</div>", unsafe_allow_html=True)


# Sources / evidence
search_results = result.get("search_results", "")
scraped_content = result.get("scraped_content", "")

urls = extract_urls(search_results)

st.markdown(
    """
    <div class="section-card">
        <div class="section-title">Research evidence</div>
        <div class="section-caption">
            The raw outputs below come directly from the existing Search Agent
            and Reader Agent.
        </div>
    """,
    unsafe_allow_html=True,
)

if urls:
    st.markdown("**Sources discovered**")
    for i, url in enumerate(urls, start=1):
        st.markdown(f"{i}. {url}")

with st.expander("Search agent output"):
    st.markdown(search_results or "No search output returned.")

with st.expander("Reader agent output"):
    st.markdown(scraped_content or "No reader output returned.")

st.markdown("</div>", unsafe_allow_html=True)


# Export
export_text = (
    f"# Multi-Agent Research Report\n\n"
    f"## Topic\n{st.session_state.get('research_topic', '')}\n\n"
    f"## Final Report\n{report}\n\n"
    f"## Critic Review\n{feedback}\n\n"
    f"## Search Agent Output\n{search_results}\n\n"
    f"## Reader Agent Output\n{scraped_content}\n"
)

st.download_button(
    "Download research output",
    data=export_text,
    file_name="research_report.md",
    mime="text/markdown",
    use_container_width=False,
)
