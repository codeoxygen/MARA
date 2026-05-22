import asyncio
from threading import Thread
from typing import Dict, Any, Callable
from app.core.logging import logger
from app.services.websocket_manager import websocket_manager
from app.schemas.websocket import WSEvent, WSNodeStatus, WSDomain
from datetime import datetime
import uuid
import time


class GraphRunner:
    """Background thread runner for LangGraph with detailed WebSocket streaming"""

    def __init__(self):
        self.running_graphs: Dict[str, Any] = {}

    def run_graph(
        self,
        session_id: str,
        graph,
        initial_state: Dict[str, Any],
        event_callback: Callable = None,
    ):
        """Run graph in background thread and broadcast detailed events"""

        def execute():
            try:
                logger.info(f"📊 Graph starting: {session_id}")
                asyncio.run(self._broadcast_graph_start(session_id))

                node_times = {}  # Track execution time per node
                current_node = None

                for event in graph.stream(initial_state):
                    # Parse event structure: {node_name: {state_dict}}
                    if isinstance(event, dict) and len(event) > 0:
                        node_name = next(iter(event))
                        node_output = event[node_name]

                        # Update state with output
                        if isinstance(node_output, dict):
                            initial_state.update(node_output)

                        # Track node execution
                        if current_node != node_name:
                            # Previous node ended
                            if current_node:
                                asyncio.run(
                                    self._broadcast_node_end(
                                        session_id,
                                        current_node,
                                        node_times.get(current_node, 0),
                                        initial_state,
                                    )
                                )

                            # New node starting
                            current_node = node_name
                            node_times[node_name] = time.time()
                            asyncio.run(self._broadcast_node_start(session_id, node_name))

                        # Broadcast processing event with current state
                        asyncio.run(
                            self._broadcast_node_processing(
                                session_id, node_name, initial_state
                            )
                        )

                    if event_callback:
                        event_callback(event)

                # Broadcast final node end
                if current_node:
                    asyncio.run(
                        self._broadcast_node_end(
                            session_id,
                            current_node,
                            node_times.get(current_node, 0),
                            initial_state,
                        )
                    )

                # Check final status
                final_status = initial_state.get("status", "unknown")
                if final_status in ("awaiting_approval", "revision_requested"):
                    logger.info(f"⏸️  Graph paused: {session_id} (waiting for approval/revision)")
                else:
                    logger.info(f"✅ Graph completed: {session_id} - Status: {final_status}")
                    asyncio.run(self._broadcast_graph_complete(session_id, initial_state))

                self.running_graphs.pop(session_id, None)

            except Exception as e:
                logger.error(f"❌ Graph execution failed: {session_id}: {e}")
                asyncio.run(self._broadcast_error(session_id, str(e)))

        thread = Thread(target=execute, daemon=True)
        self.running_graphs[session_id] = thread
        thread.start()

    async def _log_and_broadcast(self, session_id: str, ws_event: WSEvent):
        """Log streaming event and broadcast to frontend"""
        log_prefix = f"📡 STREAM [{session_id}]"
        log_msg = f"{log_prefix} {ws_event.node:20} | {ws_event.status.value:12} | {ws_event.message}"
        logger.info(log_msg)
        await websocket_manager.broadcast(session_id, ws_event)

    async def _broadcast_graph_start(self, session_id: str):
        """Broadcast graph execution started"""
        ws_event = WSEvent(
            session_id=session_id,
            node="graph",
            status=WSNodeStatus.RUNNING,
            domain=WSDomain.PLANNER,
            message="📊 Campaign planning workflow started",
            payload={"event": "graph_start"},
            timestamp=datetime.utcnow(),
        )
        await self._log_and_broadcast(session_id, ws_event)

    async def _broadcast_node_start(self, session_id: str, node_name: str):
        """Broadcast node execution starting"""
        ws_event = WSEvent(
            session_id=session_id,
            node=node_name,
            status=WSNodeStatus.RUNNING,
            domain=self._infer_domain(node_name),
            message=f"▶️  Starting {self._format_node_name(node_name)}",
            payload={"event": "node_start", "node": node_name},
            timestamp=datetime.utcnow(),
        )
        await self._log_and_broadcast(session_id, ws_event)

    async def _broadcast_node_processing(
        self, session_id: str, node_name: str, full_state: Dict
    ):
        """Broadcast node is processing"""
        status_value = full_state.get("status", "processing")

        ws_event = WSEvent(
            session_id=session_id,
            node=node_name,
            status=WSNodeStatus.PROCESSING,
            domain=self._infer_domain(node_name),
            message=f"⏳ {self._format_node_name(node_name)} processing... Status: {status_value}",
            payload={
                "event": "node_processing",
                "node": node_name,
                "current_status": status_value,
            },
            timestamp=datetime.utcnow(),
        )
        await self._log_and_broadcast(session_id, ws_event)

    async def _broadcast_node_end(
        self, session_id: str, node_name: str, start_time: float, final_state: Dict
    ):
        """Broadcast node execution completed"""
        elapsed = time.time() - start_time if start_time else 0
        status_value = final_state.get("status", "unknown")

        ws_event = WSEvent(
            session_id=session_id,
            node=node_name,
            status=WSNodeStatus.COMPLETE,
            domain=self._infer_domain(node_name),
            message=f"✅ {self._format_node_name(node_name)} completed in {elapsed:.2f}s. Status: {status_value}",
            payload={
                "event": "node_end",
                "node": node_name,
                "elapsed_seconds": round(elapsed, 2),
                "final_status": status_value,
            },
            timestamp=datetime.utcnow(),
        )
        await self._log_and_broadcast(session_id, ws_event)

    async def _broadcast_graph_complete(self, session_id: str, final_state: Dict):
        """Broadcast entire graph execution completed"""
        campaign_name = final_state.get("campaign_brief", {}).get("campaign_name", "Campaign")
        status = final_state.get("status", "complete")

        ws_event = WSEvent(
            session_id=session_id,
            node="graph",
            status=WSNodeStatus.COMPLETE,
            domain=WSDomain.PLANNER,
            message=f"🎉 Campaign '{campaign_name}' workflow complete! Status: {status}",
            payload={
                "event": "graph_complete",
                "campaign_name": campaign_name,
                "final_status": status,
            },
            timestamp=datetime.utcnow(),
        )
        await self._log_and_broadcast(session_id, ws_event)

    async def _broadcast_error(self, session_id: str, error_msg: str):
        """Broadcast error event"""
        ws_event = WSEvent(
            session_id=session_id,
            node="graph",
            status=WSNodeStatus.ERROR,
            domain=WSDomain.PLANNER,
            message=f"❌ Error: {error_msg}",
            error_message=error_msg,
            payload={"event": "error", "error": error_msg},
            timestamp=datetime.utcnow(),
        )
        await self._log_and_broadcast(session_id, ws_event)

    @staticmethod
    def _infer_domain(node_name: str) -> WSDomain:
        """Infer domain from node name"""
        if "approval" in node_name:
            return WSDomain.COMMS
        elif "analytics" in node_name:
            return WSDomain.ANALYTICS
        elif "input" in node_name:
            return WSDomain.PRE_GRAPH
        else:
            return WSDomain.PLANNER

    @staticmethod
    def _format_node_name(node_name: str) -> str:
        """Format node name for display"""
        name_map = {
            "input_validator": "Input Validation",
            "planner": "Campaign Planner",
            "approval": "Slack Approval",
            "analytics": "Analytics Report",
        }
        return name_map.get(node_name, node_name.replace("_", " ").title())


graph_runner = GraphRunner()
