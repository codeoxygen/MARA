# Slack Connection Quick Reference

## ✅ Pre-Flight Checklist

Before running campaigns, verify your Slack setup:

```bash
# 1. Check environment variables
echo "Webhook URL: $SLACK_WEBHOOK_URL"
echo "Base URL: $BASE_URL"

# Expected format:
# Webhook URL: https://hooks.slack.com/services/T.../B.../X...
# Base URL: https://your-domain-or-ngrok.com (NO trailing slash)
```

## 🧪 Test Slack Connection

```bash
# Run diagnostics endpoint
curl http://localhost:8000/api/campaigns/test/slack | jq .

# Expected response for working setup:
# {
#   "summary": "✅ Slack is properly configured and connected!",
#   "connectivity_test": {
#     "status": "success",
#     "message": "✅ Slack webhook is working!"
#   },
#   "issues": []
# }
```

## 📤 Test Full Approval Flow

```bash
# 1. Submit a test campaign
RESPONSE=$(curl -X POST http://localhost:8000/api/campaigns/run \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_name": "Slack Test",
    "objective": "Test approval flow",
    "target_audience": "Team",
    "channels": ["linkedin"],
    "duration_days": 7,
    "budget": 1000,
    "key_messages": ["Test"],
    "success_metrics": ["Engagement"],
    "additional_context": "Testing Slack integration"
  }')

CAMPAIGN_ID=$(echo $RESPONSE | jq -r '.campaign_id')
echo "Campaign ID: $CAMPAIGN_ID"

# 2. Check Slack for the approval message
# - Look for message from your bot in the configured channel
# - Should have "Approve" and "Request Revisions" buttons

# 3. Click "Approve" button
# - Should get confirmation in browser
# - Campaign should proceed to analytics

# 4. Monitor logs for approval confirmation
tail -f app.log | grep "$CAMPAIGN_ID"
```

## 🐛 Quick Troubleshooting

| Issue | Quick Fix |
|-------|-----------|
| "SLACK_WEBHOOK_URL not configured" | Add `SLACK_WEBHOOK_URL` to `.env` and restart server |
| No Slack message received | Run diagnostics: `curl http://localhost:8000/api/campaigns/test/slack` |
| Approval link doesn't work | Check `BASE_URL` is public and ngrok is running (for local dev) |
| "Invalid approval token" | Use the original Slack message button, don't modify URL |
| Timeout after 1 hour | Check that BASE_URL is accessible and approval link works |

## 📋 Slack Message Contents

The Slack message includes:

```
📋 FULL CAMPAIGN APPROVAL REQUEST

📌 CAMPAIGN DETAILS
- Name, Objective, Audience, Duration, Budget, Channels

📋 CAMPAIGN OVERVIEW
- Strategic summary

📝 CONTENT PIECES
- What will be created

🎯 ASSIGNED TASKS
- Tasks grouped by channel

🔗 ASANA PROJECT
- Link to Asana (if configured)

📊 FULL CAMPAIGN PLAN
- JSON snapshot of plan

👉 INTERACTIVE BUTTONS
- [✅ Approve] [🔄 Request Revisions]
```

## 🔗 Useful Endpoints

```bash
# Test Slack connection
GET /api/campaigns/test/slack

# Submit campaign for approval
POST /api/campaigns/run

# Get campaign status
GET /api/campaigns/{campaign_id}

# Approval response (called by Slack button)
GET /api/campaigns/{campaign_id}/approve?token={token}&action=approve
GET /api/campaigns/{campaign_id}/approve?token={token}&action=request_revisions
```

## 💡 Setup Tips

### Local Development (ngrok)

```bash
# Terminal 1: Start ngrok
ngrok http 8000

# Copy the HTTPS URL, then update .env
BASE_URL=https://abc-123-def.ngrok.io

# Terminal 2: Restart your app
uvicorn app.main:app --reload --port 8000
```

### Production

```bash
# Update .env with your real domain
BASE_URL=https://your-domain.com

# Ensure your domain is publicly accessible
# and firewall allows incoming HTTPS traffic
```

## 📊 Monitoring

```bash
# Watch approval process in real-time
tail -f app.log | grep -E "approval|Slack|token"

# Expected log sequence:
# 1. "Approval request sent"
# 2. "Awaiting approval response"
# 3. (User clicks button in Slack)
# 4. "Approval response recorded"
# 5. "Campaign APPROVED" or "revisions requested"
```

## 🆘 Getting Help

1. Run diagnostics: `curl http://localhost:8000/api/campaigns/test/slack`
2. Check logs: Look for error messages with emojis and timestamps
3. Verify config: Make sure `SLACK_WEBHOOK_URL` and `BASE_URL` are correct
4. Read docs: See `SLACK_SETUP.md` for detailed troubleshooting

## 🎯 Next Steps After Setup

1. ✅ Verify Slack connection works
2. ✅ Test full approval flow with a test campaign
3. ✅ Create real campaigns and handle approvals
4. ✅ Set up analytics dashboard (optional)
5. ✅ Integrate with Asana (optional)
