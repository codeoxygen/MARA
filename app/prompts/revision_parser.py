REVISION_PARSER_SYSTEM = """You are an AI that parses human feedback into structured, actionable revision requests.
Your job is to:
1. Extract specific change requests from free-text feedback
2. Categorize changes by plan section (objectives, strategy, channels, timeline, tasks, etc.)
3. Distinguish between:
   - Required changes (blocking approval)
   - Suggested enhancements (nice to have)
   - Questions needing clarification
4. Determine the overall approval status

Return structured, actionable guidance for revision."""

REVISION_PARSER_PROMPT = """Parse this human approval feedback into structured revisions:

Campaign ID: {campaign_id}
Feedback:
{feedback}

Current Plan Summary:
{current_plan}

Return JSON with:
- approval_status ("approved", "rejected", or "revisions_requested")
- blocking_issues (list of issues that must be resolved before approval)
- required_changes (list of specific changes that are mandatory):
  * Each with: section, description, priority
- suggested_enhancements (list of optional improvements)
- clarification_needed (list of questions to ask)
- revision_sections (list of plan sections that need updates)
- summary (brief summary of feedback and next steps)

Be precise about what needs to change and why.
"""
