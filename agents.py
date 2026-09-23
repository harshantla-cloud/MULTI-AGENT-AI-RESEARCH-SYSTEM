from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from tools import web_search, scrape_url


# Load environment variables from .env
load_dotenv()


# Initialize Gemini model
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
        tools=[scrape_url]
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
into a clear, structured, factual and insightful report.

Do not invent facts.
Use only the information available in the research.
"""
    ),
    (
        "human",
        """
Write a detailed research report on the topic below.

Topic:
{topic}

Research Gathered:
{research}

Structure the report as:

1. Introduction

2. Key Findings
   - Minimum 3 well-explained points

3. Conclusion

4. Sources
   - List all URLs found in the research

Requirements:
- Be detailed
- Be factual
- Be professional
- Use clear headings
- Do not make up information
"""
    ),
])


# Prompt → Gemini → String output
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

Your job is to carefully evaluate a research report.

Be honest, specific and objective.
Identify both strengths and weaknesses.
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

One line verdict:
...
"""
    ),
])


# Prompt → Gemini → String output
critic_chain = (
    critic_prompt
    | llm
    | StrOutputParser()
)