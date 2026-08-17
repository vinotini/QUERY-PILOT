import pandas as pd
import plotly.express as px

def create_chart(df):
    if df is None or df.empty or len(df.columns) < 2:
        return None

    x = df.columns[0]
    numeric = [
        c for c in df.columns[1:]
        if pd.api.types.is_numeric_dtype(df[c])
    ]

    if not numeric:
        return None

    y = numeric[0]

    if len(df) <= 20:
        return px.bar(df, x=x, y=y, title=f"{y} by {x}")

    return px.line(df, x=x, y=y, title=f"{y} by {x}")
