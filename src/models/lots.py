from datetime import UTC, datetime, timedelta
from .base import Model
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Numeric, Enum, ForeignKey, DateTime
from src.schemas.lots import LotStatus


class Bid(Model):
    __tablename__ = "auction_bids"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lot_id: Mapped[int] = mapped_column(ForeignKey("auction_lots.id"))
    bidder: Mapped[str]
    amount: Mapped[float] = mapped_column(Numeric(10, 2))

    lot: Mapped["Lot"] = relationship(back_populates="bids", lazy="joined")


class Lot(Model):
    __tablename__ = "auction_lots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    starting_price: Mapped[float] = mapped_column(Numeric(10, 2))
    status: Mapped[LotStatus] = mapped_column(
        Enum(LotStatus), default=LotStatus.RUNNING
    )
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    bids: Mapped[list[Bid]] = relationship(
        back_populates="lot", order_by=Bid.created_at, lazy="selectin"
    )

    @property
    def last_bid_amount(self) -> float:
        if self.bids:
            return self.bids[-1].amount
        return 0
