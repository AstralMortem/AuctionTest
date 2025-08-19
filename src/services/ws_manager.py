from typing import Dict, List
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, lot_id: int, websocket: WebSocket):
        await websocket.accept()
        if lot_id not in self.active_connections:
            self.active_connections[lot_id] = []
        self.active_connections[lot_id].append(websocket)

    def disconnect(self, lot_id: int, websocket: WebSocket):
        self.active_connections[lot_id].remove(websocket)

    async def broadcast(self, lot_id: int, message: dict):
        if lot_id in self.active_connections:
            for connection in self.active_connections[lot_id]:
                await connection.send_json(message)


manager = ConnectionManager()
