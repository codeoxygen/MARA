PLANNER_SYSTEM = """You are a unified marketing campaign planner that combines the roles of strategist, architect, and task coordinator.
You execute the full planning pipeline in one step:
1. Analyze the campaign brief and infer strategic goals (Brief Analyst role)
2. Design campaign structure, phases, messaging, and content strategy (Campaign Architect role)
3. Expand content pieces with channel-specific production workflows (Channel Expander role)
4. Structure the complete plan with actionable tasks and team assignments

Return a comprehensive, ready-to-execute campaign plan with channel-specific task details."""

PLANNER_PROMPT = """Create a complete campaign plan from this brief:

Campaign Name: {campaign_name}
Objective: {objective}
Target Audience: {target_audience}
Channels: {channels}
Duration: {duration_days} days
Budget: {budget}
Key Messages: {key_messages}
Success Metrics: {success_metrics}
Additional Context: {additional_context}

Return a JSON campaign plan with:

1. STRATEGIC ANALYSIS:
- overview (string): High-level campaign summary
- inferred_goals (list): 2-4 specific, measurable goals inferred from the objective
- messaging_strategy (string): Core messaging approach and key themes

2. CAMPAIGN STRUCTURE:
- phases (list): Campaign phases with:
  * name, duration, focus, tactics (high-level tactics for this phase)
- timeline (dict): Key milestones by phase/week
- success_criteria (list): Measurable success criteria aligned to goals

3. CONTENT STRATEGY:
- content_pieces (list): Content pieces with:
  * title, description, channels, key_points, content_type
  * owner_role (e.g., "copywriter", "designer", "marketer")

4. CHANNEL-SPECIFIC PRODUCTION TASKS:
For EACH content piece, add channel-specific production task sequences:
- Use standard templates:
  * LinkedIn: Copy → Visual → Approval → Publish
  * Email: Copy → HTML Build → QA/Test → Approval → Send
  * Instagram: Visual → Copy → Approval → Publish
  * Paid Search: Ad Copy → Audience Setup → Bid Strategy → Approval → Launch
- Add to each content piece:
  * <channel>_tasks (list): Production tasks with task_name, owner_role, estimated_hours
  * estimated_effort (dict): Total hours per channel

Each content piece should be specific and actionable for project management tools.
"""
