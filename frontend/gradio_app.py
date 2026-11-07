
import os
import gradio as gr

from agents.orchestrator import NL2SQLOrchestrator
from database.connection import test_connection
from visualization.charts import create_chart


# ============================================================
# CONFIGURATION
# ============================================================

APP_TITLE = "QUERY PILOT"
PORT = int(os.environ.get("PORT", 7860))


# ============================================================
# ORCHESTRATOR INITIALIZATION
# ============================================================

orchestrator = NL2SQLOrchestrator()


# ============================================================
# DATABASE CONNECTION STATUS
# ============================================================

try:
    test_connection()
    db_status = "🟢 Supabase PostgreSQL: CONNECTED"

except Exception as exc:
    db_status = f"🔴 Supabase PostgreSQL: ERROR - {exc}"
    print(f"Database connection error: {exc}")


# ============================================================
# RUN QUERY
# ============================================================

def run_query(question):

    if not question or not question.strip():
        return (
            "", "", "", None, None, "", "", "",
            "Please enter a question."
        )

    try:
        result = orchestrator.run(question.strip())

        # ----------------------------------------------------
        # RAG RESULTS
        # ----------------------------------------------------

        retrieved_text = "\n\n".join(
            f'TABLE: {item["table"]}\n'
            f'SCORE: {item["score"]:.4f}\n'
            f'{item["text"]}'
            for item in result.get("retrieved", [])
        )

        # ----------------------------------------------------
        # CHART GENERATION
        # ----------------------------------------------------

        chart = None

        try:
            chart = create_chart(result.get("result"))
        except Exception as chart_error:
            print(f"Chart creation failed: {chart_error}")

        # ----------------------------------------------------
        # RETURN RESULTS
        # ----------------------------------------------------

        return (
            result.get("plan", ""),
            retrieved_text,
            result.get("sql", ""),
            result.get("result"),
            chart,
            result.get("insights", ""),
            result.get("trace", ""),
            result.get("errors", ""),
            "✅ Query completed successfully."
        )

    except Exception as exc:

        print("\n========== QUERY FAILED ==========")
        print(type(exc).__name__)
        print(exc)
        print("==================================\n")

        return (
            "",
            "",
            "",
            None,
            None,
            "",
            "",
            f"{type(exc).__name__}: {exc}",
            f"❌ Query failed: {exc}"
        )


# ============================================================
# REFRESH RAG SCHEMA
# ============================================================

def refresh_schema():

    try:
        orchestrator.refresh_rag()

        return (
            "✅ Live Supabase schema refreshed "
            "and RAG index rebuilt."
        )

    except Exception as exc:

        print(f"RAG refresh failed: {exc}")

        return f"❌ Refresh failed: {exc}"


# ============================================================
# GRADIO USER INTERFACE
# ============================================================

with gr.Blocks(
    title=APP_TITLE,
    theme=gr.themes.Soft()
) as demo:

    gr.Markdown(
        """
        # 🚀 QUERY PILOT

        ### Transforming Enterprise Data Into Business Intelligence
        """
    )

    gr.Markdown(
        """
        Ask complex business questions in plain English.

        QUERY PILOT understands your enterprise data schema,
        retrieves relevant context, generates and validates SQL,
        automatically self-corrects errors, executes queries,
        and transforms raw data into meaningful visualizations
        and actionable business insights.

        **Ask → Understand → Retrieve → Generate → Validate
        → Self-Correct → Execute → Analyze → Decide**
        """
    )

    gr.Markdown(db_status)

    # ========================================================
    # QUERY INPUT
    # ========================================================

    with gr.Row():

        question = gr.Textbox(
            label="Ask your database",
            placeholder="Example: Show the top 10 products by total sales",
            lines=3,
            scale=4
        )

        run_button = gr.Button(
            "Run Query",
            variant="primary",
            scale=1
        )

    # ========================================================
    # REFRESH SCHEMA
    # ========================================================

    refresh_button = gr.Button(
        "Refresh Live Schema"
    )

    refresh_status = gr.Markdown()

    # ========================================================
    # OUTPUT TABS
    # ========================================================

    with gr.Tabs():

        with gr.Tab("Query Plan"):

            plan_output = gr.Textbox(
                lines=15,
                label="Planner Agent"
            )

        with gr.Tab("RAG"):

            rag_output = gr.Textbox(
                lines=20,
                label="Retrieved Schema"
            )

        with gr.Tab("Generated SQL"):

            sql_output = gr.Code(
                language="sql",
                label="PostgreSQL"
            )

        with gr.Tab("Results"):

            result_output = gr.Dataframe(
                interactive=False
            )

        with gr.Tab("Visualization"):

            chart_output = gr.Plot()

        with gr.Tab("AI Insights"):

            insight_output = gr.Markdown()

        with gr.Tab("Agent Trace"):

            trace_output = gr.Textbox(
                lines=15,
                label="Workflow Trace"
            )

            error_output = gr.Textbox(
                lines=10,
                label="Correction Log"
            )

        with gr.Tab("System"):

            gr.Markdown(
                """
                ### QUERY PILOT Architecture

                - Gemini LLM — Primary
                - Groq LLM — Automatic fallback
                - Live PostgreSQL Schema RAG
                - Planner Agent
                - Schema Agent
                - SQL Generator
                - SQL Validator
                - SQL Correction Agent
                - Insight Agent
                - Supabase PostgreSQL
                - Gradio Interface

                ### LLM Fallback

                Gemini
                ↓
                Gemini quota/error
                ↓
                Groq GPT-OSS 20B
                ↓
                Groq GPT-OSS 120B
                """
            )

    # ========================================================
    # OUTPUT COMPONENTS
    # ========================================================

    outputs = [
        plan_output,
        rag_output,
        sql_output,
        result_output,
        chart_output,
        insight_output,
        trace_output,
        error_output,
        refresh_status
    ]

    # ========================================================
    # BUTTON EVENTS
    # ========================================================

    run_button.click(
        fn=run_query,
        inputs=question,
        outputs=outputs
    )

    question.submit(
        fn=run_query,
        inputs=question,
        outputs=outputs
    )

    refresh_button.click(
        fn=refresh_schema,
        inputs=None,
        outputs=refresh_status
    )


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":

    print("=" * 55)
    print("       QUERY PILOT - STARTING APPLICATION")
    print("=" * 55)

    print(f"Port: {PORT}")

    demo.launch(
        server_name="0.0.0.0",
        server_port=PORT,
        share=False,
        show_error=True
    )
