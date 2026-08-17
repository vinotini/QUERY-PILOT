import pytest
from agents.validator import validate_sql

def test_select():
    assert validate_sql("SELECT 1") == "SELECT 1"

def test_with():
    assert validate_sql("WITH x AS (SELECT 1) SELECT * FROM x")

def test_insert_blocked():
    with pytest.raises(ValueError):
        validate_sql("INSERT INTO products VALUES (1)")

def test_delete_blocked():
    with pytest.raises(ValueError):
        validate_sql("DELETE FROM products")

def test_multiple_statements_blocked():
    with pytest.raises(ValueError):
        validate_sql("SELECT 1; SELECT 2")
