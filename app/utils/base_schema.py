from datetime import date
from pydantic import BaseModel, field_validator


class BaseSchema(BaseModel):

    @field_validator("*", mode="before")
    @classmethod
    def dates_to_str(cls, value):
        if isinstance(value, date):
            return str(value)
        return value