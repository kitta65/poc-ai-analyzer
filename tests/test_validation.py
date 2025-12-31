import pytest
from pydantic_ai import ModelRetry

from app.agents.graphql import validate_graphql_query

@pytest.mark.parametrize(
    "query",
    [
        (
            """\
query {
  cube {
    users {
      gender
      count
    }
  }
}"""
        ),
    ],
)
def test_validate_graphql_query_valid(query: str):
    # Should not raise any exception
    validate_graphql_query(query)


@pytest.mark.parametrize(
    "query",
    [
        # empty query
        ("",),
        # undefined field
        (
            """\
query {
  cube {
    users {
      gender
      # does not exist
      created_at {
        week
      }
    }
  }
}"""
        ),
    ],
)
def test_validate_graphql_query_invalid(query: str):
    with pytest.raises(ModelRetry):
        validate_graphql_query(query)
