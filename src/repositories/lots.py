from .base import BaseRepository
from src.models.lots import Lot, Bid
from src.core.db import SessionDep
from typing import Annotated
from fastapi import Depends


class LotRepository(BaseRepository[Lot, int]):
    model = Lot


class BidRepository(BaseRepository[Bid, int]):
    model = Bid


async def get_lot_repo(session: SessionDep):
    return LotRepository(session)


async def get_bid_repo(session: SessionDep):
    return BidRepository(session)


LotRepoDep = Annotated[LotRepository, Depends(get_lot_repo)]
BidRepoDep = Annotated[BidRepository, Depends(get_bid_repo)]
