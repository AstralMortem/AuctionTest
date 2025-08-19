from datetime import UTC, datetime, timedelta
from typing import Annotated
from fastapi import Depends
from fastapi_pagination import Params
from src.repositories.lots import LotRepository, BidRepository, LotRepoDep, BidRepoDep
from src.schemas.lots import (
    LotCreate,
    BidCreate,
    LotStatus,
    LotTimeExpandedEvent,
    LotBidPlacedEvent,
    LotEndedEvent,
)
from src.core.exceptions import AuctionError, status
from src.models.lots import Bid, Lot
from src.core.conf import settings
from src.core.db import session_factory
from src.services.ws_manager import manager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

scheduler = AsyncIOScheduler(
    timezone="UTC",
    jobstores={"default": SQLAlchemyJobStore(url=str(settings.SCHEDULER_DATABASE_URL))},
)


async def end_lot(lot_id: int):
    async with session_factory() as session:
        lot_repo = LotRepository(session)
        lot = await lot_repo.get_by_id(lot_id)
        if lot is None:
            raise AuctionError(status.HTTP_404_NOT_FOUND, "Lot not found")

        # End lot and broadcast event
        lot = await lot_repo.update(lot, {"status": LotStatus.ENDED})
        payload = LotEndedEvent(lot_id=lot.id, final_price=lot.last_bid_amount)
        await manager.broadcast(lot.id, payload.model_dump_json())
        return lot


class LotService:
    def __init__(self, lot_repo: LotRepository, bid_repo: BidRepository):
        self.lot_repo = lot_repo
        self.bid_repo = bid_repo

    async def create_lot(self, payload: LotCreate):
        # Create lot
        payload_dict = payload.model_dump()
        # Set end time
        payload_dict["end_time"] = datetime.now(UTC) + timedelta(
            seconds=payload_dict.pop("bid_duration")
        )
        lot = await self.lot_repo.create(payload_dict)
        return lot

    async def create_bid(self, lot_id: int, payload: BidCreate):
        lot = await self.get_lot(lot_id)

        # Check if lot not ended
        if lot.status == LotStatus.ENDED:
            raise AuctionError(status.HTTP_400_BAD_REQUEST, "Lot is ended")

        # Check if bid amount is greater than last bid
        if payload.amount <= lot.last_bid_amount:
            raise AuctionError(
                status.HTTP_400_BAD_REQUEST,
                f"Bid amount must be greater than last bid amount, > {lot.last_bid_amount}",
            )

        # Create bid
        payload_dict = payload.model_dump()
        payload_dict["lot_id"] = lot_id
        bid = await self.bid_repo.create(payload_dict)
        lot = await self.update_lot_time(lot, bid)

        # Broadcast bid_placed event
        event_payload = LotBidPlacedEvent(
            lot_id=lot_id, bidder=bid.bidder, amount=bid.amount
        )
        await manager.broadcast(lot_id, event_payload.model_dump_json())
        return bid

    async def get_lot(self, lot_id: int):
        # Check if lot exist
        lot = await self.lot_repo.get_by_id(lot_id)
        if lot is None:
            raise AuctionError(status.HTTP_404_NOT_FOUND, "Lot not found")
        return lot

    async def update_lot_time(self, lot: Lot, bid: Bid):
        # Update lot end time
        if lot.end_time - datetime.now() < timedelta(
            seconds=settings.DEFAULT_BID_DURATION_SECONDS
        ):
            new_lot = await self.lot_repo.update(
                lot,
                {
                    "end_time": datetime.now(UTC)
                    + timedelta(seconds=settings.DEFAULT_BID_DURATION_SECONDS)
                },
            )

            # broadcast updated lot time
            event_payload = LotTimeExpandedEvent(
                lot_id=lot.id, ended_at=new_lot.end_time
            )
            await manager.broadcast(lot.id, event_payload.model_dump_json())

            # Reschedule lot
            await self.reschedule_lot(new_lot)

            return new_lot

    async def get_lots(self, params: Params):
        lots = await self.lot_repo.get_all(params)
        return lots

    async def reschedule_lot(self, lot: Lot):
        # Remove old job and create new
        job_id = f"lot_{lot.id}"
        try:
            scheduler.remove_job(job_id)
        except Exception:
            pass

        scheduler.add_job(
            end_lot,
            "date",
            run_date=lot.end_time,
            args=[lot.id],
            id=job_id,
            misfire_grace_time=30,
        )
        return lot


async def get_lots_service(lot_repo: LotRepoDep, bid_repo: BidRepoDep):
    return LotService(lot_repo, bid_repo)


LotServiceDep = Annotated[LotService, Depends(get_lots_service)]
