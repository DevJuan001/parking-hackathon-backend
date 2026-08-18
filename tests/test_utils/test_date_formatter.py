from datetime import datetime, time
import pytest
from app.utils.date_formatter import MONTHS_ES, date_formatter, time_to_12h


# ---------- date_formatter ----------


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("2026-01-01 12:00:00", "Enero 01 2026"),
        ("2026-01-30", "Enero 30 2026"),
    ]
)
def test_date_formatter_normalizes(raw: datetime, expected: str):
    assert date_formatter(raw) == expected


def test_date_formatter_rejects_unsupported_type():
    with pytest.raises(TypeError):
        date_formatter(1234567890)


def test_MONTHS_ES_has_all_expected_keys():
    assert set(MONTHS_ES.values()) == {
        "Enero",
        "Febrero",
        "Marzo",
        "Abril",
        "Mayo",
        "Junio",
        "Julio",
        "Agosto",
        "Septiembre",
        "Octubre",
        "Noviembre",
        "Diciembre"
    }


# ---------- time_to_12h ----------

@pytest.mark.parametrize(
    "raw, expected",
    [
        (time(0, 0),  "12:00 A.M."),
        (time(0, 30), "12:30 A.M."),
        (time(11, 59), "11:59 A.M."),
        (time(12, 0), "12:00 P.M."),
        (time(13, 30), "1:30 P.M."),
        (time(23, 59), "11:59 P.M."),
        ("00:00", "12:00 A.M."),
        ("14:30", "2:30 P.M."),
        (datetime(2026, 1, 1, 15, 45), "3:45 P.M."),
    ]
)
def test_time_to_12h_normalizes(raw: time, expected: str):
    assert time_to_12h(raw) == expected


def test_time_to_12h_rejects_unsupported_type():
    with pytest.raises(TypeError):
        time_to_12h(42)
