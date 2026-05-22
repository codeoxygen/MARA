from app.services.llm_service import llm_service
from app.graph.state import GraphState
from app.core.logging import logger
from app.prompts.brief_analyst import BRIEF_ANALYST_SYSTEM, BRIEF_ANALYST_PROMPT
import json

async def analyze_brief(state: GraphState) -> GraphState:
    """Analyze campaign brief with LLM"""
    try:
        brief = state.get("campaign_brief", {})

        prompt = BRIEF_ANALYST_PROMPT.format(
            campaign_name=brief.get("campaign_name", ""),
            objective=brief.get("objective", ""),
            target_audience=brief.get("target_audience", ""),
            channels=brief.get("channels", []),
            duration_days=brief.get("duration_days", 0),
            budget=brief.get("budget", "Not specified"),
            key_messages=brief.get("key_messages", []),
            success_metrics=brief.get("success_metrics", []),
            additional_context=brief.get("additional_context", ""),
        )

        response = await llm_service.generate(
            prompt=prompt,
            system=BRIEF_ANALYST_SYSTEM,
            max_tokens=2048,
        )

        if not response or not response.strip():
            raise ValueError("Empty response from LLM")

        logger.debug(f"Raw LLM response: {response[:500]}")
        enriched = json.loads(response)
        state["enriched_brief"] = enriched
        state["status"] = "brief_analyzed"
        logger.info(f"Brief analyzed: {enriched.get('inferred_goals', [])}")

    except Exception as e:
        state["status"] = "brief_analysis_failed"
        state["error_message"] = str(e)
        logger.error(f"Brief analysis failed: {e}")

    return state
