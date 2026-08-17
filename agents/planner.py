from agents.model import ask


def create_plan(question: str) -> str:
    """
    Create a structured query plan from the user's
    natural-language request.

    No SQL is generated at this stage.
    """

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    prompt = f"""
You are the Query Planning Agent in an enterprise NL2SQL system.

Analyze the user's natural-language request and create a
structured plan for the SQL Generator.

Return EXACTLY these sections:

INTENT:
METRICS:
DIMENSIONS:
FILTERS:
TIME_RANGE:
SORTING:
LIMIT:
AMBIGUITY:

Rules:

1. Do NOT generate SQL.
2. Do NOT invent database tables or columns.
3. Identify what the user wants to know.
4. Identify numerical metrics such as:
   COUNT, SUM, AVG, MIN, MAX.
5. Identify grouping dimensions.
6. Identify requested filters.
7. Identify any requested date/time range.
8. Identify sorting requirements.
9. Identify LIMIT requirements such as top 10.
10. If the request is ambiguous, clearly state the ambiguity.
11. Keep the plan concise and structured.

User Question:
{question}
"""

    result = ask(prompt)

    if not result:
        raise RuntimeError(
            "Planner Agent returned an empty response."
        )

    return result.strip()