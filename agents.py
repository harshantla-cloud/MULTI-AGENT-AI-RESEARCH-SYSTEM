from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from tools import web_search, scrape_multiple_urls


# Load environment variables
load_dotenv()


# Initialize Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)


# ============================================================
# SEARCH AGENT
# ============================================================

def build_search_result():
    return create_agent(
        model=llm,
        tools=[web_search]
    )


# ============================================================
# READER AGENT
# ============================================================

def build_reader_agent():
    return create_agent(
        model=llm,
        tools=[scrape_multiple_urls]
    )


# ============================================================
# WRITER CHAIN
# ============================================================

writer_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are an expert research writer.

Your job is to transform gathered research
from multiple sources into a clear, structured,
factual and insightful report.

Do not invent facts.
Use only the information available in the research.
Keep source information attached to the claims.
"""
    ),
    (
        "human",
        """
Write a detailed research report on the topic below.

Topic:
{topic}

Research Gathered From Multiple Sources:
{research}

Structure the report as:

1. Introduction

2. Key Findings
   - Minimum 3 well-explained points

3. Conclusion

4. Sources
   - List all URLs found in the research

Requirements:
- Use information from multiple sources
- Be factual and professional
- Do not make up information
- Keep source URLs with the relevant information
- Use clear headings
"""
    ),
])


writer_chain = (
    writer_prompt
    | llm
    | StrOutputParser()
)


# ============================================================
# CRITIC CHAIN
# ============================================================

critic_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are a sharp and constructive research critic.

Your job is to carefully evaluate a research report
for factual quality, source usage, clarity and completeness.

Be honest, specific and objective.
"""
    ),
    (
        "human",
        """
Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

Source Quality:
- ...

One line verdict:
...
"""
    ),
])


critic_chain = (
    critic_prompt
    | llm
    | StrOutputParser()
)