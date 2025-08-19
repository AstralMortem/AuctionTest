from datetime import datetime
from enum import StrEnum
from typing import Literal
from pydantic import BaseModel
from src.core.conf import settings


class LotStatus(StrEnum):
    RUNNING = "running"
    ENDED = "ended"


LotEventType = Literal["bid_placed", "lot_ended", "lot_time_expanded"]


class LotBidPlacedEvent(BaseModel):
    type: LotEventType = "bid_placed"
    lot_id: int
    bidder: str
    amount: float


class LotEndedEvent(BaseModel):
    type: LotEventType = "lot_ended"
    lot_id: int
    final_price: float


class LotTimeExpandedEvent(BaseModel):
    type: LotEventType = "lot_time_expanded"
    lot_id: int
    ended_at: datetime


class LotCreate(BaseModel):
    title: str
    description: str | None = None
    starting_price: float
    bid_duration: int = settings.DEFAULT_BID_DURATION_SECONDS


class BidCreate(BaseModel):
    bidder: str
    amount: float


class BidRead(BaseModel):
    id: int
    bidder: str
    amount: float
    lot: "LotRead"


class LotRead(BaseModel):
    id: int
    title: str
    description: str | None = None
    starting_price: float
    status: LotStatus = LotStatus.RUNNING
    end_time: datetime
