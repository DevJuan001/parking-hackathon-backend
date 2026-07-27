from datetime import date
from typing import Optional
from pydantic import BaseModel


class FilterReservationsSchema(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
