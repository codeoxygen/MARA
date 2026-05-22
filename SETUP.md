# MARA Setup Guide

Complete step-by-step guide to set up and run MARA locally.

## Prerequisites

- Python 3.11+
- pip
- ngrok (for tunneling to Slack)
- Slack workspace with admin access
- Anthropic API key

## Step 1: Clone and Install

```bash
cd /Users/lahirujayakodi/Desktop/MARA_Agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .
```

## Step 2: Get Anthropic API Key

1. Visit https://console.anthropic.com/account/keys
2. Create or copy your API key
3. Save for later

## Step 3: Set Up Slack Webhook

### Create Slack App

1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name: "MARA Campaign Approvals"
4. Choose your workspace
5. Click "Create App"

### Enable Incoming Webhooks

1. Go to "Incoming Webhooks"
2. Toggle "Activate Incoming Webhooks" → On
3. Click "Add New Webhook to Workspace"
4. Select channel for approvals (e.g., #marketing-approvals)
5. Copy the webhook URL

## Step 4: Set Up ngrok Tunnel

```bash
# Install ngrok: https://ngrok.com/download

# Start tunnel (in a separate terminal)
ngrok http 8000

# Note the HTTPS URL (e.g., https://abc123.ngrok.io)
```

## Step 5: Configure Environment

```bash
cp .env.example .env

# Edit .env with:
# ANTHROPIC_API_KEY=sk-ant-...
# SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
# BASE_URL=https://abc123.ngrok.io
```

## Step 6: Run the Server

```bash
# In the project directory
source venv/bin/activate

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

## Step 7: Test the API

### Using curl:

```bash
curl -X POST http://localhost:8000/api/campaigns/run \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_name": "Test Campaign",
    "objective": "Test the system",
    "target_audience": "Testers",
    "channels": ["LinkedIn"],
    "duration_days": 7
  }'
```

You should get:
```json
{
  "campaign_id": "abc-123",
  "session_id": "xyz-789",
  "status": "running"
}
```

### Using Python requests:

```python
import requests

response = requests.post(
    "http://localhost:8000/api/campaigns/run",
    json={
        "campaign_name": "Test Campaign",
        "objective": "Test the system",
        "target_audience": "Testers",
        "channels": ["LinkedIn"],
        "duration_days": 7,
    }
)

print(response.json())
```

## Step 8: Monitor Execution

### Check campaign status:

```bash
curl http://localhost:8000/api/campaigns/{campaign_id}
```

### Watch WebSocket events:

```bash
# Using websocat (install: cargo install websocat)
websocat ws://localhost:8000/ws/{session_id}

# Or use a client library in Python:
import asyncio
import websockets
import json

async def watch():
    async with websockets.connect("ws://localhost:8000/ws/{session_id}") as ws:
        async for message in ws:
            print(json.dumps(json.loads(message), indent=2))

asyncio.run(watch())
```

## Step 9: Approve Campaign in Slack

1. Check your Slack channel for approval message
2. Click "✅ Approve" or "🔄 Request Revisions"
3. If approving: system continues to analytics
4. If revisions: feedback fed back to campaign architect for revision loop

## Troubleshooting

### "ModuleNotFoundError: No module named 'anthropic'"

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -e .
```

### "Failed to connect to Slack"

- Verify `SLACK_WEBHOOK_URL` is correct
- Check webhook URL has no leading/trailing spaces
- Test webhook manually:
  ```bash
  curl -X POST -H 'Content-type: application/json' \
    --data '{"text":"Test"}' \
    YOUR_WEBHOOK_URL
  ```

### WebSocket connection fails

- Verify ngrok tunnel is running
- Check BASE_URL in .env matches ngrok URL
- Ensure session_id is correct in WebSocket URL

### LLM returns errors

- Check ANTHROPIC_API_KEY is valid
- Check token limits aren't exceeded
- Review prompt in `app/prompts/`

## Next Steps

1. **Customize Prompts**: Edit agent prompts in `app/prompts/`
2. **Add Channels**: Extend `app/utils/channel_templates.py`
3. **Integrate Analytics**: Configure GA4 in `app/services/analytics_service.py`
4. **Deploy**: See README.md for Docker deployment

## Useful Commands

```bash
# Run with debug logging
LOG_LEVEL=DEBUG uvicorn app.main:app --reload

# Format code
black app/

# Lint code
ruff check app/

# Run tests
pytest tests/

# Check imports
python3 -c "from app.main import app; print('OK')"
```

## Architecture Reminders

- **Planner Domain**: Analyzes brief → Creates plan → Expands tasks → Assembles task list
- **Comms Domain**: Formats proposal → Sends to Slack → Gets approval feedback → Parses revisions
- **Analytics Domain**: Fetches metrics → Synthesizes insights
- **WebSocket**: Streams real-time graph node execution
- **HITL**: Human-in-the-loop approval via Slack

## Getting Help

- Check logs: Look for `ERROR` in server output
- Review prompts: `app/prompts/` - customize for your use case
- Inspect state: Add breakpoints in graph nodes
- Test endpoints: Use Postman or curl

Good luck! 🚀
