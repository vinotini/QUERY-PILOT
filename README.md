---
title: QUERY_PILOT
app_file: app.py
sdk: gradio
sdk_version: 6.24.0
---
# Agentic RAG NL2SQL Copilot - Full Version

This is a modular version of the uploaded NL2SQL/AI SQL Assistant.
It keeps the uploaded ecommerce schema, SQL examples, Gemini workflow,
PostgreSQL execution and Gradio concepts, while separating the system
into database, RAG, agent, visualization, evaluation and frontend modules.

Pipeline:
Question -> Planner -> Schema RAG -> SQL Generator -> Validator
-> Supabase PostgreSQL -> Self-Correction -> Results -> Visualization -> Insights

Setup:
1. Python 3.10+
2. pip install -r requirements.txt
3. Copy .env.example to .env
4. Add NEW Gemini and Supabase PostgreSQL credentials
5. python app.py

Never commit .env. Use a read-only PostgreSQL database role.
