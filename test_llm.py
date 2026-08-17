from llm import generate_with_llm

prompt = """
Convert this question into SQLite SQL.

Database schema:

customers(
    customer_id INTEGER,
    name TEXT,
    city TEXT
)

orders(
    order_id INTEGER,
    customer_id INTEGER,
    amount REAL,
    order_date TEXT
)

Relationship:
orders.customer_id = customers.customer_id

Question:
Show the top 5 customers by total sales.

Return ONLY the SQL query.
"""

sql = generate_with_llm(prompt)

print("\nFINAL SQL:")
print(sql)