"""Сначала: python -m alembic upgrade head. Сервер: python -m uvicorn main:app --reload."""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Path as PathParameter
from sqlalchemy import URL, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from db import get_session
from models import Review
from schemas import ReviewCreate, ReviewResponse

ReviewId = Annotated[int, PathParameter(gt=0)]

def create_app(database_path: Path | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        url = URL.create("sqlite+aiosqlite", database=str(app.state.database_path))
        engine = create_async_engine(url)
        app.state.session_factory = async_sessionmaker(engine, expire_on_commit=False)
        try:
            # Схему готовим заранее командой python -m alembic upgrade head.
            yield
        finally:
            await engine.dispose()

    app = FastAPI(
        title="Гостевая книга",
        description="Учебный JSON API на FastAPI, Pydantic и SQLAlchemy.",
        lifespan=lifespan,
    )
    app.state.database_path = (
        database_path if database_path is not None else Path(__file__).with_name("reviews.sqlite3")
    )

    @app.get("/reviews", response_model=list[ReviewResponse], status_code=200, tags=["Отзывы"])
    async def review_list(
        session: AsyncSession = Depends(get_session),
        author: str | None = None,
    ):
        statement = select(Review).order_by(Review.id.desc())
        if author:
            statement = statement.where(Review.author == author)
        result = await session.execute(statement)
        return result.scalars().all()

    @app.post("/reviews", response_model=ReviewResponse, status_code=201, tags=["Отзывы"])
    async def review_create(
        review: ReviewCreate,
        session: AsyncSession = Depends(get_session),
    ):
        new_review = Review(author=review.author,
                            text=review.text)
        new_review.normalize()
        if not new_review.is_valid():
            raise HTTPException(status_code=400, detail="Нельзя в качестве отзыва или автора ввести только пробелы")
        session.add(new_review)
        await session.commit()
        await session.refresh(new_review)
        return new_review

    @app.get("/reviews/{review_id}", response_model=ReviewResponse, tags=["Отзывы"])
    async def get_review_by_id(
            review_id: ReviewId,
            session: AsyncSession = Depends(get_session),
    ):
        saved_review = await session.get(Review, review_id)
        if saved_review is None:
            raise HTTPException(status_code=404, detail="Отзыв не найден")

        return saved_review

    @app.delete("/reviews/{review_id}", status_code=204, tags=["Отзывы"])
    async def delete_review_by_id(
            review_id: ReviewId,
            session: AsyncSession = Depends(get_session),
    ):
        task = await session.get(Review, review_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Отзыв не найден")

        await session.delete(task)
        await session.commit()


    return app


app = create_app()
