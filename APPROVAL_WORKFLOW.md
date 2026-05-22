# MARA Campaign Approval Workflow with Revisions

## Overview
The campaign workflow now implements a complete approval cycle where:
1. **Planner** creates a comprehensive campaign plan with all tasks
2. **Approval** sends the FULL plan to Slack and waits for human approval
3. **Revision Loop** allows stakeholders to reject and request revisions
4. **Analytics** runs only after approval is given

## Architecture

```
┌─────────────────┐
│  Input Validator │
└────────┬────────┘
         │
         ▼
┌──────────────────────────────────────────────────┐
│  PLANNER NODE                                    │
│  - Validates brief                               │
│  - Calls LLM to generate complete campaign plan  │
│  - Assembles tasks for each channel              │
│  - Creates Asana project with all tasks          │
│  - Returns: campaign_plan, assembled_tasks,      │
│    asana_project                                 │
└────────┬─────────────────────────────────────────┘
         │
    [Planning Failed?] ──YES──> END
         │ NO
         ▼
┌──────────────────────────────────────────────────┐
│  APPROVAL NODE                                   │
│  - Sends FULL campaign plan to Slack             │
│  - Includes:                                     │
│    * Campaign details (name, budget, duration)   │
│    * Campaign overview                           │
│    * All content pieces                          │
│    * All assigned tasks by channel               │
│    * Asana project link                          │
│    * Full campaign plan JSON                     │
│  - WAITS for Slack response (max 1 hour)         │
└────────┬─────────────────────────────────────────┘
         │
    [Approval Status?]
    /              \
  REJECT        APPROVE
    │              │
    ▼              ▼
BACK TO         ANALYTICS
PLANNER
    │              │
    ├──────┬───────┘
           ▼
        [Complete]
```

## Key Changes

### 1. **Graph Structure** (`app/graph/builder.py`)
- Added conditional routing after planner to handle planning failures
- Added conditional routing after approval with revision loop support
- Supports max 5 iterations (configurable in config)

```python
# Routing functions:
- _route_after_planner(): Returns "approval" if successful, END if failed
- _route_after_approval(): Returns "planner" for revisions, "analytics" for approval
```

### 2. **Approval Handler** (`app/graph/nodes/approval_handler.py`)
Completely rewritten to:
- Send **FULL campaign plan** to Slack (not just overview)
- Include all tasks organized by channel
- Include content pieces details
- Include Asana project information
- **Wait indefinitely** for Slack response (1-hour timeout)
- Poll every 2 seconds for approval_response update
- Route based on response: "approved" → analytics, "rejected" → planner

**Full Message Sent to Slack Contains:**
```
Campaign Details:
- Name, objective, target audience
- Duration, budget, channels

Campaign Overview

Content Pieces:
- Title, description, channels
- Content requirements for each channel

Assigned Tasks:
- All tasks organized by channel
- Task titles with content piece association
- Total task count and Asana link

Full Campaign Plan JSON:
- Complete JSON structure for reference
```

### 3. **Planner Node Enhancement** (`app/graph/nodes/planner.py`)
- Detects when running as initial plan vs. revision
- If revision (approval_response.status == "rejected"):
  - Reads feedback from approval_response
  - Appends feedback to prompt: `REVISION FEEDBACK: {feedback}`
  - LLM generates improved plan based on feedback
- Increments revision_count for tracking
- Better error handling for JSON parsing failures

### 4. **State Initialization** (`app/api/routes/campaigns.py`)
- Initialize campaign_plan as empty dict (not None)
- Initialize assembled_tasks and asana_project as empty dicts
- Ensures null safety throughout the workflow

### 5. **Slack Service** (`app/services/slack_service.py`)
- Enhanced error logging with response details
- Debug logging for webhook configuration
- Clear error messages when Slack send fails

### 6. **State Type** (`app/graph/state.py`)
- Added `asana_project` field to track Asana integration
- Added `approval_token` field for tracking approval requests

## Workflow States

| Status | Meaning | Next Step |
|--------|---------|-----------|
| `initialized` | Campaign created | → Planner |
| `plan_complete` | Planner finished | → Approval |
| `planning_failed` | Planner error | → END |
| `awaiting_approval` | Waiting for Slack | (polling) |
| `approved` | Stakeholder approved | → Analytics |
| `revision_requested` | Stakeholder wants changes | → Planner (revision) |
| `approval_failed` | Slack send error | → END |
| `approval_timeout` | No response in 1 hour | → END |

## Revision Cycle Details

1. **First Approval Request:**
   - Planner creates initial campaign plan
   - Sends to Slack
   - Revision count = 0

2. **Rejection:**
   - Approval handler polls and detects rejection
   - Returns status = "revision_requested"
   - Graph routes back to planner

3. **Revision Planning:**
   - Planner detects approval_response.status == "rejected"
   - Incorporates feedback into LLM prompt
   - Revision count = 1
   - Returns revised plan

4. **Re-approval:**
   - Revised plan sent to Slack (marked as "Revision #1")
   - Repeat until approved or max iterations (5)

## Testing

### 1. Test Slack Connectivity
```bash
curl http://localhost:8000/api/campaigns/test/slack
```

Response should indicate successful webhook connection.

### 2. Submit Campaign
```bash
curl -X POST http://localhost:8000/api/campaigns/run \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_name": "Test Campaign",
    "objective": "Drive awareness",
    "target_audience": "Tech enthusiasts",
    "channels": ["instagram", "email"],
    "duration_days": 30,
    "budget": 50000
  }'
```

### 3. Check Status
```bash
curl http://localhost:8000/api/campaigns/{campaign_id}
```

### 4. Submit Approval/Revision (from Slack or direct API)
```bash
# Approve
curl -X POST "http://localhost:8000/api/campaigns/{campaign_id}/approve?action=approve"

# Reject with feedback
curl -X POST "http://localhost:8000/api/campaigns/{campaign_id}/approve?action=reject&feedback=Please%20focus%20more%20on%20organic%20reach"
```

## Error Handling

**If Planner Fails:**
- Graph stops immediately after planner
- Status = "planning_failed"
- Error message logged in state

**If Slack Send Fails:**
- Approval node catches exception
- Status = "approval_failed"
- Error details logged

**If Approval Times Out:**
- After 1 hour with no response
- Status = "approval_timeout"
- Graph ends

**If Max Revisions Reached:**
- After 5 rejection cycles
- Graph proceeds to analytics even without approval
- Alternative: Return error

## Configuration

In `.env`:
```
MAX_REVISION_ITERATIONS=5  # Max approval cycles before forcing continuation
SLACK_WEBHOOK_URL=...      # Slack incoming webhook for approval messages
BASE_URL=...               # Base URL for approval buttons/links
```

## Logging

All approval events logged with consistent format:
```
📡 STREAM [session_id] approval | status | message
✋ Approval request sent for campaign X. Waiting for Slack response...
📲 Slack message with approval token: token_xxx
⏳ Still waiting for approval on X (120s elapsed)
✅ Campaign X approved by Slack (waited 45.3s)
🔄 Campaign X rejected with feedback: ...
```

## Next Steps

1. **Verify Slack connectivity** - Run test endpoint
2. **Submit test campaign** - Verify planner executes
3. **Approve in Slack** - Verify analytics runs
4. **Test revision cycle** - Reject and verify planner revises
5. **Monitor logs** - Check streaming events are logged correctly
