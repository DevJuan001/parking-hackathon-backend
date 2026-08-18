import pytest

from app.utils.round_to_50 import round_up_to_next_50


@pytest.mark.parametrize(
    "raw, expected",
    [
        (0, 50),
        (1, 50),
        (49, 50),
        (50, 50),
        (50.01, 100),
        (51, 100),
        (19990, 20000),
        (10.72, 50),
        (-10.20, 50),
    ]
)
def test_round_to_50_normalizes(raw, expected):
    assert round_up_to_next_50(raw) == expected


@pytest.mark.parametrize("value", [None, "ABC"])
def test_round_to_50_rejects_invalid_values(value):
    with pytest.raises(TypeError):
        round_up_to_next_50(value)
