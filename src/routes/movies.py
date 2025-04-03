from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.movies import MovieListResponseSchema, MovieDetailResponseSchema, MovieBase
from src.database.session import get_db
from src.database.models import MovieModel


router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("/", response_model=MovieListResponseSchema)
async def get_movies(
        page: int = Query(1, ge=1),
        per_page: int = Query(10, ge=1, le=20),
        db: AsyncSession = Depends(get_db)
) -> MovieListResponseSchema:
    if page < 1:
        raise HTTPException(
            status_code=422,
            detail=[
                {
                    "loc": ["query", "page"],
                    "msg": "ensure this value is greater than or equal to 1",
                    "type": "value_error.number.not_ge"
                },
            ]
        )

    if per_page < 1 or per_page > 20:
        raise HTTPException(
            status_code=422,
            detail=[
                {
                    "loc": ["query", "per_page"],
                    "msg": "ensure this value is greater than or equal to 1",
                }
            ]
        )
    total_stmt = select(func.count(MovieModel.id))
    total_result = await db.execute(total_stmt)
    total = total_result.scalar()

    if total == 0:
        raise HTTPException(
            status_code=404,
            detail="No movies found."
        )

    offset = (page - 1) * per_page

    movies_stmt = select(MovieModel).offset(offset).limit(per_page)
    movies_result = await db.execute(movies_stmt)
    movies = movies_result.scalars().all()

    total_pages = total // per_page + (1 if total % per_page > 0 else 0)
    prev_page = f"/movies/?page={page - 1}&per_page={per_page}" if page > 1 else None
    next_page = (
        f"/movies/?page={page + 1}&per_page={per_page}" if page < total_pages else None
    )

    if total_pages < page:
        raise HTTPException(
            status_code=404,
            detail="No movies found."
        )

    return MovieListResponseSchema(
        movies=[MovieBase.model_validate(movie) for movie in movies],
        prev_page=prev_page,
        next_page=next_page,
        total_pages=total_pages,
        total_items=total
    )


@router.get("/{movie_id}/", response_model=MovieDetailResponseSchema)
async def get_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MovieModel).where(MovieModel.id == movie_id))
    movie = result.scalar_one_or_none()
    if not movie:
        raise HTTPException(
            status_code=404,
            detail="Movie with the given ID was not found."
        )
    return MovieDetailResponseSchema.model_validate(movie)
