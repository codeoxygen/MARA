from app.services.analytics_service import analytics_service
from app.graph.state import GraphState
from app.core.logging import logger

async def fetch_metrics(state: GraphState) -> GraphState:
    """Fetch metrics from GA4 and channel APIs"""
    try:
        brief = state.get("campaign_brief", {})
        campaign_id = state.get("campaign_id")
        channels = brief.get("channels", [])

        metrics = await analytics_service.fetch_all_metrics(campaign_id, channels)

        state["metrics"] = metrics
        state["status"] = "metrics_fetched"
        logger.info(f"Metrics fetched for {len(channels)} channels")

    except Exception as e:
        state["status"] = "metrics_fetch_failed"
        state["error_message"] = str(e)
        logger.error(f"Metrics fetching failed: {e}")

    return state
