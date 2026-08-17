"""
Central LLM interface for QUERY PILOT.

All agents should call:

    from agents.model import ask

    response = ask(prompt)

The actual model routing is handled by llm.py.
"""

from llm import generate_with_llm


def ask(prompt: str) -> str:
    """
    Send a prompt to the central LLM router.

    The router automatically handles:

        Gemini
           ↓
        Groq 20B
           ↓
        Groq 120B
           ↓
        OpenRouter

    If one provider fails, the next provider is tried.
    """

    # ---------------------------------------------------------
    # Validate prompt
    # ---------------------------------------------------------

    if not isinstance(prompt, str):
        raise TypeError("Prompt must be a string.")

    if not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    # ---------------------------------------------------------
    # Call central LLM router
    # ---------------------------------------------------------

    response = generate_with_llm(prompt)

    # ---------------------------------------------------------
    # Validate response
    # ---------------------------------------------------------

    if response is None:
        raise RuntimeError("LLM returned None.")

    response = str(response).strip()

    if not response:
        raise RuntimeError("LLM returned an empty response.")

    return response