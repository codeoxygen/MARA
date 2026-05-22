REVISION_PARSER_SYSTEM = """You are an AI that parses human feedback into structured revision requests.
Your job is to:
1. Extract specific change requests from free-text feedback
2. Identify which plan sections need revision
3. Flag any blocking concerns
4. Suggest concrete next steps

Return structured revision guidance."""

REVISION_PARSER_PROMPT = """Parse this approval feedback into structured revisions:

Campaign: {campaign_id}
Feedback: {feedback}
Current Plan: {current_plan}

Return JSON with:
- revision_sections (list of sections to revise)
- specific_changes (list of requested changes)
- blocking_issues (list of issues blocking approval)
- recommended_revisions (list of suggested changes)
- status (approved, rejected, or revisions_requested)
"""
