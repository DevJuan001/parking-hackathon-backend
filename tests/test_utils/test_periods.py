from app.utils.periods import daily_periods, period_map


def test_period_map_has_all_expected_keys():
    assert set(period_map.keys()) == {"15d", "1w", "30d", "1m", "6m", "1y"}


def test_period_map_values_are_valid_mysql_intervals():
    valid_units = {"DAY", "WEEK", "MONTH", "YEAR"}

    for key, value in period_map.items():
        parts = value.split()

        assert len(
            parts
        ) == 2, f"{key!r}: esperaba '<N> <UNIT>', recibio {value!r}"
        assert parts[1] in valid_units, f"{key!r}: unidad MySql inválida {parts[1]!r}"
        assert parts[0].isdigit(), f"{key!r}: el número no es entero {parts[0]!r}"


def test_daily_periods_matches_documented_keys():
    assert daily_periods == {"1w", "15d"}