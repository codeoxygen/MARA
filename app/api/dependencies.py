"""FastAPI dependencies"""

from app.services import LLMService, SlackService, AnalyticsService, WebSocketManager, GraphRunner
from app.graph import build_graph

def get_llm_service() -> LLMService:
    from app.services.llm_service import llm_service
    return llm_service

def get_slack_service() -> SlackService:
    from app.services.slack_service import slack_service
    return slack_service

def get_analytics_service() -> AnalyticsService:
    from app.services.analytics_service import analytics_service
    return analytics_service

def get_websocket_manager() -> WebSocketManager:
    from app.services.websocket_manager import websocket_manager
    return websocket_manager

def get_graph_runner() -> GraphRunner:
    from app.services.graph_runner import graph_runner
    return graph_runner

def get_graph():
    return build_graph()
