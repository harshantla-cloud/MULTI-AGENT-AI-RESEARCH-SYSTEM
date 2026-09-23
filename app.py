import streamlit as st
from pipeline import run_research_pipeline


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Multi-Agent Research System",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>
        .title {
            font-size: 42px;
            font-weight: 700;
            text-align: center;
            margin-bottom: 5px;
        }

        .subtitle {
            text-align: center;
            color: #777;
            font-size: 18px;
            margin-bottom: 30px;
        }

        .agent-box {
            padding: 20px;
            border: 1px solid #444;
            border-radius: 12px;
            text-align: center;
            min-height: 150px;
        }

        .agent-icon {
            font-size: 35px;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="title">🤖 Multi-Agent Research System</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Search → Scrape → Write → Critique'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# AGENT PIPELINE
# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        """
        <div class="agent-box">
            <div class="agent-icon">🔎</div>
            <h3>Search Agent</h3>
            <p>Finds recent and reliable information from the web.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div class="agent-box">
            <div class="agent-icon">🌐</div>
            <h3>Reader Agent</h3>
            <p>Selects and scrapes relevant web resources.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        """
        <div class="agent-box">
            <div class="agent-icon">✍️</div>
            <h3>Writer Chain</h3>
            <p>Creates a structured research report.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        """
        <div class="agent-box">
            <div class="agent-icon">🧐</div>
            <h3>Critic Chain</h3>
            <p>Reviews the report and provides feedback.</p>
        </div>
        """,
        unsafe_allow_html=True
    )


st.divider()


# ============================================================
# INPUT
# ============================================================

st.subheader("🔍 Enter Research Topic")

topic = st.text_input(
    "Research Topic",
    placeholder="Example: Impact of Generative AI on Software Engineering",
    label_visibility="collapsed"
)


# ============================================================
# RUN BUTTON
# ============================================================

run = st.button(
    "🚀 Start Research",
    type="primary",
    use_container_width=True
)


# ============================================================
# RUN PIPELINE
# ============================================================

if run:

    if not topic.strip():
        st.warning("Please enter a research topic.")
        st.stop()

    topic = topic.strip()

    st.divider()

    st.info("🤖 Multi-agent research pipeline is running...")

    progress = st.progress(0)

    try:

        # ----------------------------------------------------
        # STEP 1
        # ----------------------------------------------------

        progress.progress(10)
        st.write("🔎 **Search Agent:** Searching the web...")

        # ----------------------------------------------------
        # Run COMPLETE pipeline
        # ----------------------------------------------------

        state = run_research_pipeline(topic)

        # ----------------------------------------------------
        # Complete
        # ----------------------------------------------------

        progress.progress(100)

        st.success("✅ Research completed successfully!")

        # Save result
        st.session_state["research_state"] = state
        st.session_state["topic"] = topic

    except Exception as e:

        st.error("❌ Something went wrong while running the pipeline.")

        st.exception(e)


# ============================================================
# DISPLAY RESULTS
# ============================================================

if "research_state" in st.session_state:

    state = st.session_state["research_state"]

    st.divider()

    st.header(
        f"📚 Research Results: {st.session_state['topic']}"
    )


    # ========================================================
    # TABS
    # ========================================================

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "🔎 Search Results",
            "🌐 Scraped Content",
            "📝 Final Report",
            "🧐 Critic Review"
        ]
    )


    # ========================================================
    # SEARCH RESULTS
    # ========================================================

    with tab1:

        st.subheader("Search Agent Output")

        search_results = state.get(
            "search_results",
            "No search results found."
        )

        st.markdown(search_results)


    # ========================================================
    # SCRAPED CONTENT
    # ========================================================

    with tab2:

        st.subheader("Reader Agent Output")

        scraped_content = state.get(
            "scraped_content",
            "No scraped content found."
        )

        st.text_area(
            "Scraped Content",
            scraped_content,
            height=600,
            label_visibility="collapsed"
        )


    # ========================================================
    # FINAL REPORT
    # ========================================================

    with tab3:

        st.subheader("📝 Final Research Report")

        report = state.get(
            "report",
            "No report generated."
        )

        st.markdown(report)

        st.download_button(
            label="⬇️ Download Research Report",
            data=report,
            file_name="research_report.md",
            mime="text/markdown"
        )


    # ========================================================
    # CRITIC REVIEW
    # ========================================================

    with tab4:

        st.subheader("🧐 Critic Chain Output")

        feedback = state.get(
            "feedback",
            "No critic feedback found."
        )

        st.markdown(feedback)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ System")

    st.markdown(
        """
        ### Pipeline

        **1.** 🔎 Search Agent

        ↓

        **2.** 🌐 Reader Agent

        ↓

        **3.** ✍️ Writer Chain

        ↓

        **4.** 🧐 Critic Chain
        """
    )

    st.divider()

    st.caption(
        "Gemini + LangChain + Tavily + BeautifulSoup + Streamlit"
    )