from llm import generate_with_llm


def generate_insights(question, dataframe):
    """
    Generate business insights from the SQL query result.

    Uses the centralized LLM router:

        Gemini
          ↓ 429 / error
        Groq GPT-OSS 20B
          ↓ failure
        Groq GPT-OSS 120B
    """

    # ========================================================
    # EMPTY RESULT
    # ========================================================

    if dataframe is None or dataframe.empty:
        return "No data was returned."

    # Limit the amount of data sent to the LLM
    sample = dataframe.head(100).to_string(index=False)

    # ========================================================
    # INSIGHT PROMPT
    # ========================================================

    prompt = f"""
You are an expert business analytics insight agent.

Analyze ONLY the data returned by the PostgreSQL query.

========================
USER QUESTION
========================

{question}

========================
QUERY RESULT
========================

{sample}

========================
INSTRUCTIONS
========================

Provide exactly these three sections:

1. Main Finding
   - State the most important result from the data.

2. Important Pattern / Comparison
   - Identify meaningful trends, differences, rankings,
     or comparisons visible in the data.

3. Useful Observation
   - Give one practical observation based only on the
     provided result.

STRICT RULES:

- Do not invent facts.
- Do not invent numbers.
- Do not assume information that is not present.
- Use only the provided query result.
- If the data does not support a conclusion, say so.
- Keep the response concise and business-focused.
"""

    # ========================================================
    # GEMINI → GROQ FALLBACK
    # ========================================================

    insights = generate_with_llm(prompt)

    if not insights:
        return "Unable to generate insights."

    return insights.strip()
