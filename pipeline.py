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
    """Convert LangChain / Gemini responses into clean text."""

    if response is None:
        return ""

    if isinstance(response, str):
        return response

    if hasattr(response, "content"):
        return extract_text(response.content)

    if isinstance(response, dict):

        if "text" in response:
            return str(response["text"])

        if "content" in response:
            return extract_text(response["content"])

        if "messages" in response:
            messages = response["messages"]

            if messages:
                return extract_text(messages[-1])

        return str(response)

    if isinstance(response, list):

        text_parts = []

        for item in response:

            if isinstance(item, str):
                text_parts.append(item)

            elif isinstance(item, dict):

                if "text" in item:
                    text_parts.append(str(item["text"]))

            elif hasattr(item, "content"):
                text_parts.append(
                    extract_text(item.content)
                )

        return "\n\n".join(text_parts)

    return str(response)


# ============================================================
# URL EXTRACTOR
# ============================================================

def extract_urls(search_results):
    """Extract unique URLs from Search Agent output."""

    urls = []

    for line in search_results.splitlines():

        line = line.strip()

        if line.startswith("URL:"):

            url = line.replace("URL:", "", 1).strip()

            if url and url not in urls:
                urls.append(url)

    return urls


# ============================================================
# MAIN RESEARCH PIPELINE
# ============================================================

def run_research_pipeline(topic: str) -> dict:

    state = {}


    # ========================================================
    # STEP 1 — SEARCH AGENT
    # ========================================================

    print("\n" + "=" * 60)
    print("STEP 1 - SEARCH AGENT")
    print("=" * 60)

    print("\nSearching multiple sources...")

    search_agent = build_search_result()

    search_result = search_agent.invoke(
        {
            "messages": [
                (
                    "user",
                    f"""
Find multiple recent, reliable and relevant sources
about the following research topic:

{topic}

Return at least 4-5 useful sources.

For every source provide:

- Source title
- URL
- Short description of why it is relevant

Prefer reliable and authoritative sources.
"""
                )
            ]
        }
    )

    state["search_results"] = extract_text(
        search_result["messages"][-1]
    )

    print("\nSEARCH RESULTS:\n")
    print(state["search_results"])


    # ========================================================
    # STEP 2 — EXTRACT MULTIPLE SOURCE URLs
    # ========================================================

    print("\n" + "=" * 60)
    print("STEP 2 - SOURCE SELECTION")
    print("=" * 60)

    urls = extract_urls(
        state["search_results"]
    )

    # Use maximum 3 sources for scraping
    selected_urls = urls[:3]

    if not selected_urls:
        raise ValueError(
            "No valid source URLs found in search results."
        )

    print("\nSelected sources:")

    for i, url in enumerate(
        selected_urls,
        start=1
    ):
        print(f"{i}. {url}")


    # ========================================================
    # STEP 3 — MULTI-SOURCE READER AGENT
    # ========================================================

    print("\n" + "=" * 60)
    print("STEP 3 - MULTI-SOURCE READER AGENT")
    print("=" * 60)

    print("\nReading multiple sources...")

    reader_agent = build_reader_agent()

    urls_text = "\n".join(
        selected_urls
    )

    reader_prompt = f"""
You are a research reader agent.

Research topic:

{topic}

The Search Agent selected these sources:

{urls_text}

Use the available multi-source scraping tool to
scrape and read ALL of these URLs.

Do not skip a source unless it cannot be accessed.

After scraping, extract the most important factual
information from each source.

Keep the sources clearly separated.

Return the result in this format:

SOURCE 1
URL: ...
Key Evidence:
- ...
- ...
- ...

SOURCE 2
URL: ...
Key Evidence:
- ...
- ...
- ...

SOURCE 3
URL: ...
Key Evidence:
- ...
- ...
- ...

Requirements:

- Use all accessible sources
- Do not invent information
- Keep source URLs
- Focus only on information relevant to the topic
- Ignore irrelevant content
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

    state["scraped_content"] = extract_text(
        reader_result["messages"][-1]
    )

    print("\nMULTI-SOURCE CONTENT:\n")
    print(state["scraped_content"])


    # ========================================================
    # STEP 4 — WRITER CHAIN
    # ========================================================

    print("\n" + "=" * 60)
    print("STEP 4 - WRITER CHAIN")
    print("=" * 60)

    print("\nGenerating research report...")

    research_combined = f"""
RESEARCH TOPIC:
{topic}


SEARCH RESULTS:
{state["search_results"]}


MULTI-SOURCE EVIDENCE:
{state["scraped_content"]}
"""

    writer_result = writer_chain.invoke(
        {
            "topic": topic,
            "research": research_combined
        }
    )

    state["report"] = extract_text(
        writer_result
    )

    print("\nFINAL REPORT:\n")
    print(state["report"])


    # ========================================================
    # STEP 5 — CRITIC CHAIN
    # ========================================================

    print("\n" + "=" * 60)
    print("STEP 5 - CRITIC CHAIN")
    print("=" * 60)

    print("\nReviewing research report...")

    critic_result = critic_chain.invoke(
        {
            "report": state["report"]
        }
    )

    state["feedback"] = extract_text(
        critic_result
    )

    print("\nCRITIC REVIEW:\n")
    print(state["feedback"])


    # ========================================================
    # PIPELINE COMPLETE
    # ========================================================

    print("\n" + "=" * 60)
    print("MULTI-SOURCE RESEARCH PIPELINE COMPLETED")
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

        print("\n\nMULTI-SOURCE CONTENT:")
        print(result["scraped_content"])

        print("\n\nFINAL REPORT:")
        print(result["report"])

        print("\n\nCRITIC REVIEW:")
        print(result["feedback"])