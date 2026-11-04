import pytest
from multiagent.agents.database import validate_readonly_sql

def test_select_allowed():
    assert validate_readonly_sql("SELECT id FROM products") == "SELECT id FROM products"

@pytest.mark.parametrize("query", [
    "DELETE FROM users", "UPDATE users SET is_active = false", "DROP TABLE users",
    "SELECT 1; DELETE FROM users", "SELECT * FROM pg_catalog.pg_tables", "CREATE TABLE x(id int)",
])
def test_unsafe_sql_rejected(query):
    with pytest.raises(ValueError):
        validate_readonly_sql(query)
