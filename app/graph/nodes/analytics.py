"""Analytics node: Fetch mock Google Analytics data and generate report"""
from app.services.mock_analytics_service import mock_analytics_service
from app.graph.state import GraphState
from app.core.logging import logger


async def analytics(state: GraphState) -> GraphState:
    """Fetch campaign analytics and generate performance report"""
    try:
        logger.info("Analytics: Fetching campaign metrics")

        campaign_name = state.get("campaign_brief", {}).get("campaign_name", "Campaign")
        campaign_id = state.get("campaign_id")

        # Fetch mock analytics
        metrics = await mock_analytics_service.fetch_campaign_metrics(campaign_id, campaign_name)

        # Build report
        report = {
            "campaign_id": campaign_id,
            "campaign_name": campaign_name,
            "metrics": metrics,
            "generated_at": __import__("datetime").datetime.utcnow().isoformat(),
        }

        state["metrics"] = metrics
        state["performance_report"] = report
        state["status"] = "complete"

        logger.info(f"Analytics: ✅ Report generated - ROI: {metrics['performance_summary']['roi_estimate']}")

    except Exception as e:
        state["status"] = "analytics_failed"
        state["error_message"] = str(e)
        logger.error(f"Analytics: Failed: {e}")

    return state
