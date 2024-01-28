from pydantic import BaseModel, Field
from typing import Optional


class Location(BaseModel):
    room: str
    bookcase: str
    shelf: str
    cuvette: str
    column: str
    row: str


class Part(BaseModel):
    serial_number: str = Field(...)
    name: str = Field(...)
    description: str = Field(...)
    category: str = Field(...)
    quantity: int = Field(...)
    price: float = Field(...)
    location: Location


class UpdatePart(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[float] = None
    location: Optional[Location] = None
