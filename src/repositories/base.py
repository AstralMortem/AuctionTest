from src.models.base import Model
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Any, TypeVar, Generic
from fastapi_pagination.bases import AbstractPage, AbstractParams
from fastapi_pagination.ext.sqlalchemy import paginate

M = TypeVar("M", bound=Model)
ID = TypeVar("ID")


class BaseRepository(Generic[M, ID]):
    model: type[M]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: ID) -> M | None:
        return await self.session.get(self.model, id)

    async def get_by_field(self, field: str, value: Any) -> M | None:
        qs = select(self.model).filter_by(**{field: value})
        return await self.session.scalar(qs)

    async def create(self, payload: dict) -> M:
        obj = self.model(**payload)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def update(self, instance: M, payload: dict) -> M:
        for key, value in payload.items():
            setattr(instance, key, value)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def delete(self, instance: M) -> None:
        await self.session.delete(instance)
        await self.session.commit()

    async def get_all(
        self, params: AbstractParams, filters: dict | None = None
    ) -> AbstractPage[M]:
        qs = select(self.model)
        if filters:
            qs = qs.filter_by(**filters)
        return await paginate(self.session, qs, params)
