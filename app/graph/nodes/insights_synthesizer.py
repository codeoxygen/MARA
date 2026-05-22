from app.services.llm_service import llm_service
from app.graph.state import GraphState
from app.core.logging import logger
from app.prompts.insights_synthesizer import (
    INSIGHTS_SYNTHESIZER_SYSTEM,
    INSIGHTS_SYNTHESIZER_PROMPT,
)
import json

async def synthesize_insights(state: GraphState) -> GraphState:
    """Synthesize metrics into insights and recommendations"""
    try:
        brief = state.get("campaign_brief", {})
        enriched = state.get("enriched_brief", {})
        metrics = state.get("metrics", {})

        prompt = INSIGHTS_SYNTHESIZER_PROMPT.format(
            campaign_name=brief.get("campaign_name", ""),
            goals=enriched.get("inferred_goals", []),
            metrics=json.dumps(metrics, indent=2),
        )

        response = await llm_service.generate(
            prompt=prompt,
            system=INSIGHTS_SYNTHESIZER_SYSTEM,
            max_tokens=2000,
        )

        insights = json.loads(response)
        state["performance_report"] = {
            "campaign_id": state.get("campaign_id"),
            "campaign_name": brief.get("campaign_name", ""),
            **insights,
        }
        state["status"] = "complete"
        logger.info("Insights synthesized, pipeline complete")

    except Exception as e:
        state["status"] = "insights_synthesis_failed"
        state["error_message"] = str(e)
        logger.error(f"Insights synthesis failed: {e}")

    return state
