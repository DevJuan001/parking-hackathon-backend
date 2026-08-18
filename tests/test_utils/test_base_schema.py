from datetime import date

from app.utils.base_schema import BaseSchema


class _ModelWithDate(BaseSchema):
    start_date: str


class _ModelWithManyDates(BaseSchema):
    start_date: str
    end_date: str


class _ModelMixed(BaseSchema):
    start_date: str
    number: int
    text: str


def test_model_converts_date_to_iso_string():
    model = _ModelWithDate.model_validate({
        "start_date": date(2026, 1, 12),
    })

    assert model.start_date == "2026-01-12"


def test_base_schema_applies_to_all_fields():
    model = _ModelWithManyDates.model_validate({
        "start_date": date(2026, 1, 12),
        "end_date": date(2028, 12, 24),
    })

    assert model.start_date == "2026-01-12"
    assert model.end_date == "2028-12-24"


def test_base_schema_does_not_touch_other_type():
    model = _ModelMixed.model_validate({
        "start_date": date(2026, 1, 20),
        "number": 100,
        "text": "Test",
    })

    assert model.start_date == "2026-01-20"
    assert model.number == 100
    assert model.text == "Test"
