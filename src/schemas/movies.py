import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class MovieBase(BaseModel):
    id: int
    name: str
    date: datetime.date
    score: float
    genre: str
    overview: str
    crew: str
    orig_title: str
    status: str
    orig_lang: str
    budget: float
    revenue: float
    country: str

    model_config = ConfigDict(from_attributes=True)


class MovieListResponseSchema(BaseModel):
    movies: list[MovieBase]
    prev_page: Optional[str] = None
    next_page: Optional[str] = None
    total_pages: int | None = None
    total_items: int | None = None


class MovieDetailResponseSchema(MovieBase):
    pass
