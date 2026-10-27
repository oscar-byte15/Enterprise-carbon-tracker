
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class ActivityCreate(BaseModel):
    category: Literal[
        "electricity",
        "heating",
        "transport",
        "waste"
    ]
    type: str
    amount: float = Field(gt=0)
    unit: str
    date: date
