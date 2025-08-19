from fastapi import APIRouter, Depends
from fastapi_pagination import Page, Params
from src.schemas.lots import BidRead, LotCreate, LotRead, BidCreate
from src.services.lots import LotServiceDep


lot_router = APIRouter(prefix="/lots", tags=["Lots"])


@lot_router.post("/", response_model=LotRead)
async def create_lot(payload: LotCreate, service: LotServiceDep):
    return await service.create_lot(payload)


@lot_router.get("/", response_model=Page[LotRead])
async def get_lots(service: LotServiceDep, params: Params = Depends()):
    return await service.get_lots(params)


@lot_router.post("/{lot_id}/bids", response_model=BidRead)
async def make_bid(lot_id: int, payload: BidCreate, service: LotServiceDep):
    return await service.create_bid(lot_id, payload)
