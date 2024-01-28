from pydantic import BaseModel, Field


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
