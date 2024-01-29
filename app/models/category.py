from pydantic import BaseModel, Field
from typing import Optional


class Category(BaseModel):
    name: str = Field(...)
    parent_name: str = Field()


class UpdateCategory(BaseModel):
    name: Optional[str] = None
    parent_name: Optional[str] = None
