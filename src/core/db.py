from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from .conf import settings
from fastapi import Depends
from typing import Annotated


engine = create_async_engine(str(settings.DATABASE_URL))
session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    async with session_factory() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


SessionDep = Annotated[AsyncSession, Depends(get_session)]
