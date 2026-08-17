import os
from dotenv import load_dotenv
from google import genai
from groq import Groq
from openai import OpenAI

load_dotenv()


# ============================================================
# CONFIGURATION
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)

# Groq fallback models
GROQ_MODELS = [
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b"
]

# OpenRouter fallback
OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "openrouter/free"
)


# ============================================================
# CLIENTS
# ============================================================

gemini_client = None
groq_client = None
openrouter_client = None


# Gemini
if GEMINI_API_KEY:
    gemini_client = genai.Client(
        api_key=GEMINI_API_KEY
    )


# Groq
if GROQ_API_KEY:
    groq_client = Groq(
        api_key=GROQ_API_KEY
    )


# OpenRouter
if OPENROUTER_API_KEY:
    openrouter_client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY
    )


# ============================================================
# SYSTEM PROMPT
# ============================================================

SQL_SYSTEM_PROMPT = """
You are an expert enterprise NL2SQL assistant.

Your task is to generate valid PostgreSQL SQL.

IMPORTANT RULES:

1. Use ONLY the tables and columns provided in the prompt.
2. Never invent tables.
3. Never invent columns.
4. Use valid PostgreSQL syntax.
5. Generate only read-only SQL.
6. SELECT and WITH queries are allowed.
7. Never generate INSERT, UPDATE, DELETE, DROP,
   CREATE, ALTER, TRUNCATE, GRANT, or REVOKE.
8. Return ONLY the SQL query.
9. Do not explain the SQL.
"""


# ============================================================
# GEMINI
# ============================================================

def try_gemini(prompt):

    if gemini_client is None:
        raise RuntimeError(
            "Gemini API key is not configured."
        )

    print("\n==============================")
    print("Trying Gemini")
    print(f"Model: {GEMINI_MODEL}")
    print("==============================")

    response = gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    print("Gemini succeeded.")

    return response.text.strip()


# ============================================================
# GROQ
# ============================================================

def try_groq(prompt):

    if groq_client is None:
        raise RuntimeError(
            "Groq API key is not configured."
        )

    for model in GROQ_MODELS:

        try:

            print("\n==============================")
            print("Trying Groq")
            print(f"Model: {model}")
            print("==============================")

            response = groq_client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": SQL_SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0
            )

            result = response.choices[0].message.content

            if not result:
                raise RuntimeError(
                    f"{model} returned an empty response."
                )

            print(f"Groq succeeded: {model}")

            return result.strip()

        except Exception as e:

            print(f"Groq failed: {model}")
            print(e)

            print("Trying next Groq model...")


    raise RuntimeError(
        "All Groq models failed."
    )


# ============================================================
# OPENROUTER
# ============================================================

def try_openrouter(prompt):

    if openrouter_client is None:
        raise RuntimeError(
            "OpenRouter API key is not configured."
        )

    print("\n==============================")
    print("Trying OpenRouter")
    print(f"Model: {OPENROUTER_MODEL}")
    print("==============================")

    response = openrouter_client.chat.completions.create(
        model=OPENROUTER_MODEL,
        messages=[
            {
                "role": "system",
                "content": SQL_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    result = response.choices[0].message.content

    if not result:
        raise RuntimeError(
            "OpenRouter returned an empty response."
        )

    print("OpenRouter succeeded.")

    return result.strip()


# ============================================================
# MAIN LLM ROUTER
# ============================================================

def generate_with_llm(prompt):

    if not prompt or not prompt.strip():
        raise ValueError(
            "Prompt cannot be empty."
        )

    errors = []


    # ========================================================
    # 1. GEMINI
    # ========================================================

    try:

        return try_gemini(prompt)

    except Exception as e:

        print("\n❌ Gemini failed:")
        print(e)

        errors.append(
            f"Gemini: {type(e).__name__}: {e}"
        )

        print("\n➡️ Switching to Groq...")


    # ========================================================
    # 2. GROQ
    # ========================================================

    try:

        return try_groq(prompt)

    except Exception as e:

        print("\n❌ Groq failed:")
        print(e)

        errors.append(
            f"Groq: {type(e).__name__}: {e}"
        )

        print("\n➡️ Switching to OpenRouter...")


    # ========================================================
    # 3. OPENROUTER
    # ========================================================

    try:

        return try_openrouter(prompt)

    except Exception as e:

        print("\n❌ OpenRouter failed:")
        print(e)

        errors.append(
            f"OpenRouter: {type(e).__name__}: {e}"
        )


    # ========================================================
    # EVERYTHING FAILED
    # ========================================================

    error_message = "\n".join(errors)

    raise RuntimeError(
        "All LLM providers failed.\n\n"
        + error_message
    )