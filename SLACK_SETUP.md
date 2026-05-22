# Slack Integration Setup Guide

MARA uses Slack to send campaign approval requests with interactive buttons for approval or revision requests. This guide covers setup, configuration, and troubleshooting.

## Quick Start

### 1. Create or Get Your Slack App

1. Go to https://api.slack.com/apps
2. Click **Create New App** → **From scratch**
3. Name it: `MARA` (or your preferred name)
4. Select your Slack workspace
5. Click **Create App**

### 2. Enable Incoming Webhooks

1. In your app's left sidebar, click **Incoming Webhooks**
2. Toggle **Activate Incoming Webhooks** to ON
3. Click **Add New Webhook to Workspace**
4. Select the channel where approval requests should be sent
5. Click **Allow**
6. Copy the **Webhook URL** (looks like: `https://hooks.slack.com/services/T.../B.../X...`)

### 3. Configure Environment Variables

Add to your `.env` file:

```env
# Slack Configuration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
BASE_URL=https://your-ngrok-url.ngrok.io  # or your production domain
```

### 4. For Approval Response Handling (Optional)

1. In your app's left sidebar, click **OAuth & Permissions**
2. Under **Bot Token Scopes**, add:
   - `chat:write`
   - `reactions:read`
3. Copy the **Bot User OAuth Token** (starts with `xoxb-`)
4. Add to `.env`: `SLACK_BOT_TOKEN=xoxb-...`

## How It Works

### Approval Flow

```
1. User submits campaign brief via API
   ↓
2. MARA generates campaign plan
   ↓
3. Approval request sent to Slack
   ↓
4. Slack message with "Approve" / "Request Revisions" buttons
   ↓
5. User clicks button
   ↓
6. Approval response sent back to API endpoint
   ↓
7. Campaign proceeds or revisions are created
```

### Slack Message Structure

When MARA sends an approval request to Slack, it includes:

- **Campaign Details**: Name, objective, audience, channels, duration, budget
- **Campaign Overview**: Strategic summary
- **Content Pieces**: What will be created
- **Task Summary**: All tasks grouped by channel
- **Asana Project Link**: Link to the Asana project (if created)
- **Full Campaign Plan**: JSON snapshot of the plan
- **Action Buttons**: Approve or Request Revisions

### Approval Button URLs

The approval buttons point to:
```
https://BASE_URL/api/campaigns/{campaign_id}/approve?token={approval_token}&action=approve
https://BASE_URL/api/campaigns/{campaign_id}/approve?token={approval_token}&action=request_revisions
```

The system validates the token to ensure only authorized responses are accepted.

## Configuration Details

### Required Environment Variables

| Variable | Example | Purpose |
|----------|---------|---------|
| `SLACK_WEBHOOK_URL` | `https://hooks.slack.com/services/T.../B.../X...` | Post messages to Slack |
| `BASE_URL` | `https://your-domain.ngrok.io` | Build approval links that point back to your API |

### Optional Environment Variables

| Variable | Example | Purpose |
|----------|---------|---------|
| `SLACK_BOT_TOKEN` | `xoxb-...` | Read message reactions (for future enhancements) |

### Using ngrok for Local Development

```bash
# Start ngrok (assuming app runs on localhost:8000)
ngrok http 8000

# Copy the HTTPS URL (e.g., https://abc-123-def.ngrok.io)
# Add to .env:
BASE_URL=https://abc-123-def.ngrok.io
```

**Note**: ngrok URLs change when you restart. Update `BASE_URL` in `.env` each time.

## Testing the Connection

### 1. Run the Diagnostics Endpoint

```bash
curl http://localhost:8000/api/campaigns/test/slack
```

This returns a comprehensive diagnostic report including:
- Configuration status
- Webhook connectivity test
- Issues found (if any)
- Recommendations

Example response:
```json
{
  "timestamp": "2025-05-22T10:00:00Z",
  "configuration": {
    "webhook_url_configured": true,
    "webhook_url_preview": "https://hooks.slack.com/services/T.../B.../...",
    "base_url": "https://your-ngrok-url.ngrok.io",
    "base_url_valid": true
  },
  "connectivity_test": {
    "status": "success",
    "message": "✅ Slack webhook is working!"
  },
  "issues": [],
  "summary": "✅ Slack is properly configured and connected!"
}
```

### 2. Submit a Test Campaign

```bash
curl -X POST http://localhost:8000/api/campaigns/run \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_name": "Test Campaign",
    "objective": "Test MARA approval flow",
    "target_audience": "QA team",
    "channels": ["linkedin", "email"],
    "duration_days": 7,
    "budget": 5000,
    "key_messages": ["Test message"],
    "success_metrics": ["Engagement rate"],
    "additional_context": "This is a test campaign"
  }'
```

This returns:
```json
{
  "campaign_id": "abc-123-def",
  "session_id": "xyz-789",
  "status": "running"
}
```

You should receive a Slack message in your configured channel within seconds.

## Troubleshooting

### Issue: "SLACK_WEBHOOK_URL not configured"

**Problem**: Slack messages are not being sent.

**Solution**:
1. Check that `SLACK_WEBHOOK_URL` is set in `.env`
2. Make sure the URL is not commented out
3. Verify the URL starts with `https://hooks.slack.com`
4. Run the diagnostics endpoint to confirm

### Issue: "Approval timeout after 3600s"

**Problem**: The system is waiting for a Slack approval response but never receives it.

**Possible Causes**:
1. The Slack message was never sent (check above)
2. The user didn't click the Approve/Revisions button
3. The approval link is broken or inaccessible
4. `BASE_URL` is incorrect or not publicly accessible

**Solution**:
1. Run the diagnostics endpoint to check connection
2. Verify `BASE_URL` is set correctly and is publicly accessible
3. For local development, ensure ngrok is running and `BASE_URL` points to the current ngrok URL
4. Check the Slack channel to see if the message was posted
5. Test the approval URL directly in a browser: `https://BASE_URL/api/campaigns/{campaign_id}` to verify it's accessible

### Issue: "Invalid approval token"

**Problem**: The approval button returns a 403 Forbidden error.

**Possible Causes**:
1. The token was tampered with
2. The campaign_id doesn't match
3. The request is from a different session

**Solution**:
1. Ensure you're clicking the button from the original Slack message
2. Don't modify the URL manually
3. Check that the campaign_id and token are correct in the request

### Issue: Slack message appears but buttons don't work

**Problem**: Buttons are visible but clicking them gives an error.

**Solution**:
1. Check that `BASE_URL` is accessible from your network
2. For local dev, ensure ngrok is running: `ngrok http 8000`
3. Update `.env` with the current ngrok URL
4. Restart your API server
5. Submit a new campaign and test again

### Issue: "Webhook returned HTTP 403"

**Problem**: Slack is rejecting the webhook URL.

**Possible Causes**:
1. The webhook URL is invalid or expired
2. The channel no longer exists
3. The Slack app was reinstalled

**Solution**:
1. Generate a new webhook URL from https://api.slack.com/apps
2. Update `SLACK_WEBHOOK_URL` in `.env`
3. Restart your API server
4. Run the diagnostics endpoint to confirm

### Issue: ngrok is blocked or rate limited

**Problem**: Slack cannot reach your API through ngrok.

**Solution**:
1. Use a paid ngrok plan for more bandwidth
2. For production, use a real domain instead of ngrok
3. Check firewall/network rules

## Approval Response Handling

When a user clicks "Approve" or "Request Revisions":

1. The browser follows the button URL
2. The request is sent to: `/api/campaigns/{campaign_id}/approve?token=...&action=...`
3. The system validates the token
4. The approval response is recorded in the campaign state
5. The approval_handler node detects the response and:
   - If approved: Proceeds to analytics
   - If revisions requested: Loops back to campaign architect for revisions

The user gets a confirmation response in their browser.

## Advanced Configuration

### Custom Slack Channel per Campaign

To send different campaigns to different channels, you would need:
1. Multiple webhook URLs (one per channel)
2. Logic to select the appropriate webhook based on campaign properties

This is not currently implemented in MARA. Open an issue if you need this feature.

### Slack Reactions as Approval (Future Enhancement)

Instead of buttons, future versions could support:
- User reacts with ✅ to approve
- User reacts with 🔄 to request revisions

This would require:
- Enabling Slack events API
- Implementing reaction listeners
- Storing message IDs for mapping reactions back to campaigns

## Integration with Other Services

### Asana Integration

MARA can create tasks in Asana and include the project URL in the Slack message. Ensure Asana service is configured if you want this feature.

### Email Notifications (Future)

Future versions may also send approval requests via email alongside Slack.

## Security Considerations

1. **Token Validation**: All approval requests require a valid token that matches the campaign's approval_token
2. **Environment Variables**: Never commit `.env` with real credentials to version control
3. **HTTPS**: Always use HTTPS URLs for `BASE_URL` in production
4. **Webhook URLs**: Rotate webhook URLs periodically for added security
5. **Rate Limiting**: Consider implementing rate limiting on the approval endpoint for production

## Support

For issues or questions:
1. Run the diagnostics endpoint: `GET /api/campaigns/test/slack`
2. Check application logs for detailed error messages
3. Verify configuration matches this guide
4. Test basic Slack connectivity before running campaigns

## Related Documentation

- [README.md](README.md) - Overview of MARA
- [README-2.md](README-2.md) - Detailed workflow documentation
- [APPROVAL_WORKFLOW.md](APPROVAL_WORKFLOW.md) - Approval workflow specifics
