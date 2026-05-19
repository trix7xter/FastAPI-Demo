from typing import Any, Generic, TypeVar

from sqlalchemy import delete, insert, select

from app.database import Base, async_session_maker

ModelType = TypeVar("ModelType", bound=Base)


class BaseDAO(Generic[ModelType]):
    model: type[ModelType]

    @classmethod
    async def find_by_id(cls, model_id: int) -> ModelType | None:
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(id=model_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def find_one_or_none(cls, **filter_by) -> ModelType | None:
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def find_all(cls, *args: Any, **kwargs: Any) -> Any:
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**kwargs)
            result = await session.execute(query)
            return list(result.scalars().all())

    @classmethod
    async def add(cls, *args: Any, **kwargs: Any) -> Any:
        async with async_session_maker() as session:
            query = insert(cls.model).values(**kwargs)
            await session.execute(query)
            await session.commit()

    @classmethod
    async def delete(cls, **filter_by) -> None:
        async with async_session_maker() as session:
            query = delete(cls.model).filter_by(**filter_by)
            await session.execute(query)
            await session.commit()
