from agents import (
    build_reader_agent,
    build_search_result,
    writer_chain,
    critic_chain
)


# ============================================================
# RESPONSE TEXT EXTRACTOR
# ============================================================

def extract_text(response):
    """
    Convert LangChain / Gemini structured responses
    into clean plain text.
    """

    if response is None:
        return ""

    # --------------------------------------------------------
    # Case 1: Already a normal string
    # --------------------------------------------------------

    if isinstance(response, str):
        return response

    # --------------------------------------------------------
    # Case 2: LangChain AIMessage / HumanMessage
    # --------------------------------------------------------

    if hasattr(response, "content"):
        return extract_text(response.content)

    # --------------------------------------------------------
    # Case 3: Dictionary
    # --------------------------------------------------------

    if isinstance(response, dict):

        # Example:
        # {"type": "text", "text": "some text"}

        if "text" in response:
            return str(response["text"])

        # Example:
        # {"content": "some text"}

        if "content" in response:
            return extract_text(response["content"])

        # Example:
        # Agent result containing messages

        if "messages" in response:
            messages = response["messages"]

            if messages:
                return extract_text(messages[-1])

        return str(response)

    # --------------------------------------------------------
    # Case 4: List of Gemini content blocks
    # --------------------------------------------------------

    if isinstance(response, list):

        text_parts = []

        for item in response:

            # Plain string
            if isinstance(item, str):
                text_parts.append(item)

            # Gemini content block
            elif isinstance(item, dict):

                if "text" in item:
                    text_parts.append(str(item["text"]))

            # Another LangChain message
            elif hasattr(item, "content"):
                text_parts.append(
                    extract_text(item.content)
                )

        return "\n\n".join(text_parts)

    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    return str(response)


# ============================================================
# MAIN RESEARCH PIPELINE
# ============================================================

def run_research_pipeline(topic: str) -> dict:

    # Dictionary containing every pipeline output
    state = {}


    # ========================================================
    # STEP 1 — SEARCH AGENT
    # ========================================================

    print("\n" + "=" * 60)
    print("STEP 1 - SEARCH AGENT")
    print("=" * 60)

    print("\nSearching the web...")

    # Create Search Agent
    search_agent = build_search_result()

    # Ask Search Agent to research the topic
    search_result = search_agent.invoke(
        {
            "messages": [
                (
                    "user",
                    f"""
Find recent, reliable and detailed information about:

{topic}

Use reliable sources and provide useful factual information
for a research report.
"""
                )
            ]
        }
    )

    # Extract only clean text
    state["search_results"] = extract_text(
        search_result["messages"][-1]
    )

    print("\nSEARCH RESULTS:\n")
    print(state["search_results"])


    # ========================================================
    # STEP 2 — READER AGENT
    # ========================================================

    print("\n" + "=" * 60)
    print("STEP 2 - READER AGENT")
    print("=" * 60)

    print("\nReading and scraping relevant sources...")

    # Create Reader Agent
    reader_agent = build_reader_agent()

    # Give Search Agent output to Reader Agent
    reader_prompt = f"""
You are a research reader agent.

Research topic:
{topic}

Below are the search results collected by another agent:

--------------------------------------------------
SEARCH RESULTS
--------------------------------------------------

{state["search_results"][:4000]}

--------------------------------------------------

Your task:

1. Identify the most relevant source or URL.
2. Use the available scraping/web tool.
3. Read the source carefully.
4. Extract important factual information.
5. Return a clean summary of the useful content.
6. Do not return Python objects, metadata, signatures,
   or unnecessary tool information.

Focus only on information useful for answering:

{topic}
"""

    reader_result = reader_agent.invoke(
        {
            "messages": [
                (
                    "user",
                    reader_prompt
                )
            ]
        }
    )

    # Extract clean text
    state["scraped_content"] = extract_text(
        reader_result["messages"][-1]
    )

    print("\nSCRAPED CONTENT:\n")
    print(state["scraped_content"])


    # ========================================================
    # STEP 3 — WRITER CHAIN
    # ========================================================

    print("\n" + "=" * 60)
    print("STEP 3 - WRITER CHAIN")
    print("=" * 60)

    print("\nGenerating research report...")

    # Combine all research
    research_combined = f"""
RESEARCH TOPIC:
{topic}


SEARCH RESULTS:
{state["search_results"]}


DETAILED SCRAPED CONTENT:
{state["scraped_content"]}
"""

    # Generate report
    writer_result = writer_chain.invoke(
        {
            "topic": topic,
            "research": research_combined
        }
    )

    # Convert AIMessage / structured response to text
    state["report"] = extract_text(
        writer_result
    )

    print("\nFINAL REPORT:\n")
    print(state["report"])


    # ========================================================
    # STEP 4 — CRITIC CHAIN
    # ========================================================

    print("\n" + "=" * 60)
    print("STEP 4 - CRITIC CHAIN")
    print("=" * 60)

    print("\nReviewing research report...")

    # Send report to critic
    critic_result = critic_chain.invoke(
        {
            "report": state["report"]
        }
    )

    # Convert response to clean text
    state["feedback"] = extract_text(
        critic_result
    )

    print("\nCRITIC REVIEW:\n")
    print(state["feedback"])


    # ========================================================
    # PIPELINE COMPLETE
    # ========================================================

    print("\n" + "=" * 60)
    print("RESEARCH PIPELINE COMPLETED")
    print("=" * 60)

    return state


# ============================================================
# RUN DIRECTLY FROM TERMINAL
# ============================================================

if __name__ == "__main__":

    print("\n")
    print("=" * 60)
    print("       MULTI-AGENT RESEARCH SYSTEM")
    print("=" * 60)

    topic = input(
        "\nEnter a research topic: "
    ).strip()

    if not topic:

        print("\nPlease enter a valid research topic.")

    else:

        result = run_research_pipeline(topic)

        print("\n")
        print("=" * 60)
        print("FINAL OUTPUT")
        print("=" * 60)

        print("\n\nSEARCH RESULTS:")
        print(result["search_results"])

        print("\n\nSCRAPED CONTENT:")
        print(result["scraped_content"])

        print("\n\nFINAL REPORT:")
        print(result["report"])

        print("\n\nCRITIC REVIEW:")
        print(result["feedback"])