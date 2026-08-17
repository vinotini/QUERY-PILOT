import gradio as gr

from agents.orchestrator import NL2SQLOrchestrator
from database.connection import test_connection
from visualization.charts import create_chart


# ============================================================
# ORCHESTRATOR
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


# ============================================================
# RUN QUERY
# ============================================================

def run_query(question):

    if not question or not question.strip():

        return (
            "",
            "",
            "",
            None,
            None,
            "",
            "",
            "Please enter a question.",
            "Query failed: Empty question."
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
        # CHART
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

        print("\n===================================")
        print("QUERY FAILED")
        print("===================================")
        print(type(exc).__name__)
        print(exc)
        print("===================================\n")

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
# REFRESH RAG
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
# GRADIO UI
# ============================================================

with gr.Blocks(title="QUERY PILOT") as demo:

    gr.Markdown(
        """
        # QUERY PILOT

        ### Transforming Enterprise Data Into Business Intelligence
        """
    )

    gr.Markdown(
        """
        Ask complex business questions in plain English.

        QUERY PILOT understands your enterprise data schema, retrieves
        relevant context, generates and validates SQL, automatically
        self-corrects errors, executes queries, and transforms raw data
        into meaningful visualizations and actionable business insights.

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
            lines=3
        )

        run_button = gr.Button(
            "Run Query",
            variant="primary"
        )

    # ========================================================
    # RAG REFRESH
    # ========================================================

    refresh_button = gr.Button(
        "Refresh Live Schema"
    )

    refresh_status = gr.Markdown()

    # ========================================================
    # OUTPUT TABS
    # ========================================================

    with gr.Tabs():

        # ----------------------------------------------------
        # QUERY PLAN
        # ----------------------------------------------------

        with gr.Tab("Query Plan"):

            plan_output = gr.Textbox(
                lines=15,
                label="Planner Agent"
            )

        # ----------------------------------------------------
        # RAG
        # ----------------------------------------------------

        with gr.Tab("RAG"):

            rag_output = gr.Textbox(
                lines=20,
                label="Retrieved Schema"
            )

        # ----------------------------------------------------
        # SQL
        # ----------------------------------------------------

        with gr.Tab("Generated SQL"):

            sql_output = gr.Code(
                language="sql",
                label="PostgreSQL"
            )

        # ----------------------------------------------------
        # RESULTS
        # ----------------------------------------------------

        with gr.Tab("Results"):

            result_output = gr.Dataframe(
                interactive=False
            )

        # ----------------------------------------------------
        # VISUALIZATION
        # ----------------------------------------------------

        with gr.Tab("Visualization"):

            chart_output = gr.Plot()

        # ----------------------------------------------------
        # AI INSIGHTS
        # ----------------------------------------------------

        with gr.Tab("AI Insights"):

            insight_output = gr.Markdown()

        # ----------------------------------------------------
        # AGENT TRACE
        # ----------------------------------------------------

        with gr.Tab("Agent Trace"):

            trace_output = gr.Textbox(
                lines=15,
                label="Workflow Trace"
            )

            error_output = gr.Textbox(
                lines=10,
                label="Correction Log"
            )

        # ----------------------------------------------------
        # SYSTEM
        # ----------------------------------------------------

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
                - Gradio UI

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
    # OUTPUT LIST
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
    # EVENTS
    # ========================================================

    run_button.click(
        run_query,
        inputs=question,
        outputs=outputs
    )

    question.submit(
        run_query,
        inputs=question,
        outputs=outputs
    )

    refresh_button.click(
        refresh_schema,
        inputs=None,
        outputs=refresh_status
    )


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":
    demo.launch()