"""WebSocket endpoint for real-time graph streaming"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.api.dependencies import get_websocket_manager
from app.core.logging import logger

router = APIRouter(tags=["websocket"])

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    session_id: str,
    websocket: WebSocket,
    ws_manager=Depends(get_websocket_manager),
):
    """WebSocket endpoint for real-time graph event streaming"""
    await ws_manager.connect(session_id, websocket)
    logger.info(f"WebSocket connected: {session_id}")

    try:
        while True:
            data = await websocket.receive_text()
            logger.debug(f"Received from {session_id}: {data}")
    except WebSocketDisconnect:
        await ws_manager.disconnect(session_id, websocket)
        logger.info(f"WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for {session_id}: {e}")
        await ws_manager.disconnect(session_id, websocket)
