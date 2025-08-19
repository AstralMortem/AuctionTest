from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.services.lots import LotServiceDep
from src.services.ws_manager import manager


ws_router = APIRouter(prefix="/ws/lots", tags=["WS"])


@ws_router.websocket("/{lot_id}")
async def websocket_endpoint(websocket: WebSocket, lot_id: int, service: LotServiceDep):
    # Check if lot exist
    await service.get_lot(lot_id)
    await manager.connect(lot_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(lot_id, websocket)
