import re

from app.utils.uuid import generate_uuid

_UUID_V4 = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)


def test_generate_uuid_matches_regex_v4():
    assert _UUID_V4.match(generate_uuid())


def test_generate_uuid_is_unique_across_calls():
    ids = {generate_uuid() for _ in range(1000)}
    assert len(ids) == 1000
