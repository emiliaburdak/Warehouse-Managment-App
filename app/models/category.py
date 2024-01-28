from pydantic import BaseModel, Field


class Category(BaseModel):
    name: str = Field(...)
    parent_name: str = Field()



