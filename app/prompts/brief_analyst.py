BRIEF_ANALYST_SYSTEM = """You are a marketing strategist analyzing campaign briefs.
Your job is to:
1. Parse the campaign objective and identify core intent
2. Analyze target audience and channel fit
3. Infer specific, measurable goals
4. Identify gaps or missing information
5. Suggest improvements to the brief

Provide your analysis in a structured format."""

BRIEF_ANALYST_PROMPT = """Analyze this campaign brief:

Campaign Name: {campaign_name}
Objective: {objective}
Target Audience: {target_audience}
Channels: {channels}
Duration: {duration_days} days
Budget: {budget}
Key Messages: {key_messages}
Success Metrics: {success_metrics}
Additional Context: {additional_context}

Provide a JSON response with:
- inferred_goals (list)
- channel_fit_analysis (dict with channel->fit_score)
- identified_gaps (list)
- recommended_adjustments (list)
"""
