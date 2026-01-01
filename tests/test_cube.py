from datetime import datetime
from typing import Any

import pytest

from app.cube import _flatten_dict


@pytest.mark.parametrize(
    "input_,expected",
    [
        # as is
        (
            {"count_user": 1, "gender": "male"},
            {"count_user": 1, "gender": "male"},
        ),
        # nested
        (
            {"orders": {"created_at": {"day": "2019-01-16T00:00:00.000Z"}}},
            {"orders__created_at__day": "2019-01-16T00:00:00.000Z"},
        ),
    ],
)
def test_flatten_dict(input_: dict[str, Any], expected: dict[str, Any]):
    actual = _flatten_dict(input_)
    assert actual == expected
