from typing import Dict, Set
from fastapi import WebSocket
from app.core.logging import logger
import json
from app.schemas.websocket import WSEvent

class WebSocketManager:
    """Manages WebSocket connections for real-time graph streaming"""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        self.active_connections[session_id].add(websocket)
        logger.info(f"WebSocket connected: {session_id}")

    async def disconnect(self, session_id: str, websocket: WebSocket):
        """Close WebSocket connection"""
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        logger.info(f"WebSocket disconnected: {session_id}")

    async def broadcast(self, session_id: str, event: WSEvent):
        """Broadcast event to all connections for a session"""
        if session_id not in self.active_connections:
            return

        disconnected = set()
        for websocket in self.active_connections[session_id]:
            try:
                await websocket.send_json(event.model_dump(mode="json"))
            except Exception as e:
                logger.error(f"Error broadcasting to {session_id}: {e}")
                disconnected.add(websocket)

        for websocket in disconnected:
            await self.disconnect(session_id, websocket)

    async def send_personal(self, session_id: str, message: dict):
        """Send message to all connections of a session"""
        if session_id not in self.active_connections:
            return

        for websocket in self.active_connections[session_id]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message: {e}")

websocket_manager = WebSocketManager()
