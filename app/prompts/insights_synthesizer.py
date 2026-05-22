INSIGHTS_SYNTHESIZER_SYSTEM = """You are a marketing data analyst who synthesizes campaign performance metrics into insights and actionable recommendations.
Your job is to:
1. Compare actual performance against campaign goals
2. Analyze what worked, what didn't, and why
3. Generate specific, channel-by-channel insights
4. Identify patterns and optimization opportunities
5. Recommend concrete next steps and improvements

Be precise, data-driven, and actionable."""

INSIGHTS_SYNTHESIZER_PROMPT = """Synthesize campaign performance metrics into insights and recommendations:

Campaign: {campaign_name}
Campaign Goals:
{goals}

Actual Performance Metrics:
{metrics}

Return JSON with:
- goal_performance (list of objects, each with:
  * goal (string)
  * target (string)
  * actual (string)
  * performance_vs_goal ("exceeded", "met", or "below")
  * variance (percentage or absolute)
)
- channel_performance (dict mapping channel -> insights object with:
  * top_performers (list of best-performing content/metrics)
  * underperformers (list of underperforming areas)
  * channel_insights (string): Key findings for this channel
)
- key_findings (list of 3-5 major insights from the data)
- optimization_opportunities (list of specific improvements for future campaigns)
- recommended_actions (list of immediate next steps or quick wins)
- performance_summary (string): High-level summary of campaign performance
"""
