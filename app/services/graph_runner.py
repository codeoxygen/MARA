import asyncio
from threading import Thread
from typing import Dict, Any, Callable
from app.core.logging import logger
from app.services.websocket_manager import websocket_manager
from app.schemas.websocket import WSEvent, WSNodeStatus, WSDomain
from datetime import datetime
import uuid

class GraphRunner:
    """Background thread runner for LangGraph with WebSocket broadcasting"""

    def __init__(self):
        self.running_graphs: Dict[str, Any] = {}

    def run_graph(
        self,
        session_id: str,
        graph,
        initial_state: Dict[str, Any],
        event_callback: Callable = None,
    ):
        """Run graph in background thread and broadcast events"""

        def execute():
            try:
                logger.info(f"Starting graph execution: {session_id}")

                for event in graph.stream(initial_state):
                    # Update the initial_state with the latest state from the event
                    if isinstance(event, dict) and len(event) > 0:
                        first_key = next(iter(event))
                        if isinstance(event[first_key], dict):
                            initial_state.update(event[first_key])

                    if event_callback:
                        event_callback(event)

                    # Broadcast to WebSocket clients
                    asyncio.run(self._broadcast_event(session_id, event))

                logger.info(f"Graph execution completed: {session_id}")
                self.running_graphs.pop(session_id, None)

            except Exception as e:
                logger.error(f"Graph execution failed: {session_id}: {e}")
                asyncio.run(
                    self._broadcast_error(session_id, str(e))
                )

        thread = Thread(target=execute, daemon=True)
        self.running_graphs[session_id] = thread
        thread.start()

    async def _broadcast_event(self, session_id: str, event: Dict[str, Any]):
        """Convert graph event to WebSocket event and broadcast"""
        node_name = event.get("node", "unknown")
        status = WSNodeStatus.COMPLETE

        ws_event = WSEvent(
            session_id=session_id,
            node=node_name,
            status=status,
            domain=self._infer_domain(node_name),
            payload=event.get("output", {}),
            timestamp=datetime.utcnow(),
        )

        await websocket_manager.broadcast(session_id, ws_event)

    async def _broadcast_error(self, session_id: str, error_msg: str):
        """Broadcast error event"""
        ws_event = WSEvent(
            session_id=session_id,
            node="graph",
            status=WSNodeStatus.ERROR,
            domain=WSDomain.PLANNER,
            error_message=error_msg,
            timestamp=datetime.utcnow(),
        )
        await websocket_manager.broadcast(session_id, ws_event)

    @staticmethod
    def _infer_domain(node_name: str) -> WSDomain:
        """Infer domain from node name"""
        if "approval" in node_name or "proposal" in node_name or "revision" in node_name:
            return WSDomain.COMMS
        elif "metrics" in node_name or "insights" in node_name:
            return WSDomain.ANALYTICS
        elif "input" in node_name:
            return WSDomain.PRE_GRAPH
        else:
            return WSDomain.PLANNER

graph_runner = GraphRunner()
