def test_database_import():
    from database.connection import engine
    assert engine is not None
