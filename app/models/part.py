from typing import Optional

from pydantic import BaseModel, Field


class Location(BaseModel):
    room: str = Field(...)
    bookcase: str = Field(...)
    shelf: str = Field(...)
    cuvette: str = Field(...)
    column: int = Field(...)
    row: int = Field(...)


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
