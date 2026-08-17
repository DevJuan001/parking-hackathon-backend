import pytest

from app.utils.plate_formatter import plate_formatter


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("ABC-123", "ABC123"),  # Strip "#"
        ("abc 123", "ABC123"),  # Strip " " y UpperCase
        ("  abc123", "ABC123"),  # Strip espacios vacíos
        ("ab-c12-3", "ABC123"),  # Multiples "-"
        ("", ""),  # Vacía
        ("ABC123", "ABC123"),  # Ya formateada
    ]
)
def test_plate_formatter_normalizes(raw: str, expected: str) -> None:
    assert plate_formatter(raw) == expected
