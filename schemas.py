"""Pydantic описывает HTTP-данные. ORM-модель находится отдельно в models.py."""

from pydantic import BaseModel, ConfigDict, Field


class ReviewCreate(BaseModel):
    author: str = Field(min_length=1, max_length=120)
    text: str = Field(min_length=1, max_length=10000)


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    author: str
    text: str
