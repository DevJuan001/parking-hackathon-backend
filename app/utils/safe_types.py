import re
from typing import Optional
from pydantic.fields import FieldInfo
from pydantic import AfterValidator, Field


_HTML_TAG = re.compile(r"<\s*/?\s*[a-zA-Z][^>]*>")
_SCRIPT_PROTOCOL = re.compile(r"javascript\s*:", re.IGNORECASE)
_EVENT_HANDLER = re.compile(r"\bon[a-zA-Z]+\s*=", re.IGNORECASE)
_SQLI_LIKE = re.compile(r"(--|;|\bunion\s+select\b|\bor\s+1\s*=\s*1\b)", re.IGNORECASE)
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

_DANGEROUS_PATTERNS = (
    _HTML_TAG,
    _SCRIPT_PROTOCOL,
    _EVENT_HANDLER,
    _SQLI_LIKE,
    _CONTROL_CHARS,
)


def _validate(
    value: Optional[str],
    *,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
) -> Optional[str]:
    if value is None:
        return None

    if not isinstance(value, str):
        raise ValueError("Por favor ingresa un texto válido.")

    stripped = value.strip()

    for pattern in _DANGEROUS_PATTERNS:
        if pattern.search(stripped):
            raise ValueError(
                "Por favor evita usar código o caracteres especiales en este campo."
            )

    if min_length is not None and len(stripped) < min_length:
        raise ValueError(
            f"Este campo necesita al menos {min_length} caracteres."
        )

    if max_length is not None and len(stripped) > max_length:
        raise ValueError(
            f"Este campo admite como máximo {max_length} caracteres."
        )

    return stripped


def safe_str(*, min_length: Optional[int] = None, max_length: int = 100) -> FieldInfo:
    def _validator(value: Optional[str]) -> Optional[str]:
        return _validate(value, min_length=min_length, max_length=max_length)

    field = Field(...)
    field.metadata.append(AfterValidator(_validator))
    return field


def safe_optional_str(*, min_length: Optional[int] = None, max_length: int = 100) -> FieldInfo:
    def _validator(value: Optional[str]) -> Optional[str]:
        return _validate(value, min_length=min_length, max_length=max_length)

    field = Field(default=None)
    field.metadata.append(AfterValidator(_validator))
    return field


def safe_list_str(
    *,
    min_length: Optional[int] = None,
    max_length: int = 100,
    min_items: int = 0,
    max_items: int = 50,
) -> FieldInfo:
    def _list_validator(value: list) -> list:
        return [
            _validate(item, min_length=min_length, max_length=max_length)
            for item in value
        ]

    field = Field(..., min_length=min_items, max_length=max_items)
    field.metadata.append(AfterValidator(_list_validator))
    return field


def safe_optional_list_str(
    *,
    min_length: Optional[int] = None,
    max_length: int = 100,
    min_items: int = 0,
    max_items: int = 50,
) -> FieldInfo:
    def _list_validator(value: Optional[list]) -> Optional[list]:
        if value is None:
            return None
        return [
            _validate(item, min_length=min_length, max_length=max_length)
            for item in value
        ]

    field = Field(default=None, min_length=min_items, max_length=max_items)
    field.metadata.append(AfterValidator(_list_validator))
    return field
