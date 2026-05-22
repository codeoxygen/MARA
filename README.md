# MARA - Marketing Agentic Resource Assistant

A production-ready multi-agent AI system that transforms marketing briefs into executable campaign plans with real-time progress tracking via WebSocket and Slack-based human approval workflows.

## Quick Start

### 1. Install Dependencies

```bash
pip install -e .
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys and Slack webhook URL
```

Required environment variables:
- `ANTHROPIC_API_KEY` - Your Anthropic API key
- `SLACK_WEBHOOK_URL` - Slack incoming webhook for approval notifications
- `BASE_URL` - Your ngrok URL (e.g., https://example.ngrok.io)

### 3. Run the Server

```bash
uvicorn app.main:app --reload --port 8000
```

Server will be available at `http://localhost:8000`

## Architecture Overview

### Graph Workflow

The system uses LangGraph to orchestrate a multi-domain agent pipeline:

**Planner Domain** (Campaign Planning)
- Input Validator: Schema validation
- Brief Analyst: Enriches brief with LLM analysis
- Campaign Architect: Generates structured campaign plan
- Channel Expander: Expands content into channel-specific tasks
- Task Assembler: Creates unified task list with dependencies

**Comms Domain** (Human Approval)
- Proposal Formatter: Transforms plan into readable proposal
- Approval Handler: Sends to Slack for human review
- Revision Parser: Structures feedback into actionable revisions
- Revision Loop: Cycles back to architect if revisions needed

**Analytics Domain** (Performance)
- Metrics Fetcher: Gathers GA4 and channel metrics
- Insights Synthesizer: Generates insights and recommendations

### Stream Architecture

- **LangGraph Integration**: Uses LangChain ChatAnthropic for LLM calls with streaming support
- **WebSocket Streaming**: Real-time node execution events to frontend
- **Token Streaming**: LLM outputs streamed token-by-token for live generation visibility
- **Slack HITL**: Approval workflow via interactive Slack buttons

## API Endpoints

### Campaign Management

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/campaigns/run` | Submit brief, start graph, get session_id |
| `GET` | `/api/campaigns/{campaign_id}` | Get campaign state snapshot |
| `POST` | `/api/campaigns/{campaign_id}/approve` | Submit approval/revision response |
| `WS` | `/ws/{session_id}` | Stream real-time execution events |

### Health

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Service status |
| `GET` | `/health` | Health check |

## Using the API

### 1. Start a Campaign

```bash
curl -X POST http://localhost:8000/api/campaigns/run \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_name": "Q3 Product Launch",
    "objective": "Drive awareness and signups for new product",
    "target_audience": "Tech-savvy professionals, 25-45",
    "channels": ["LinkedIn", "Email", "Paid Search"],
    "duration_days": 30,
    "budget": 50000,
    "key_messages": ["Revolutionary approach", "Limited early access"],
    "success_metrics": ["1000 qualified leads", "5% conversion rate"],
    "additional_context": "Targeting B2B SaaS buyers"
  }'
```

Response:
```json
{
  "campaign_id": "abc-123",
  "session_id": "xyz-789",
  "status": "running"
}
```

### 2. Listen to Real-Time Events

```bash
websocat ws://localhost:8000/ws/{session_id}
```

Events streamed:
```json
{
  "session_id": "xyz-789",
  "node": "brief_analyst",
  "status": "running",
  "domain": "planner",
  "payload": {...},
  "timestamp": "2025-05-22T10:00:00Z"
}
```

### 3. Handle Approval via Slack

- System sends formatted proposal to Slack
- Click "Approve" or "Request Revisions" button
- Feedback captured and processed through revision loop
- Graph resumes automatically or redirects to architect

### 4. Get Campaign State

```bash
curl http://localhost:8000/api/campaigns/{campaign_id}
```

## Configuration

### Application Settings

- `APP_ENV`: development | production
- `LOG_LEVEL`: DEBUG | INFO | WARNING | ERROR
- `MAX_REVISION_ITERATIONS`: Max approval revision attempts (default: 5)
- `WEBSOCKET_MAX_SIZE`: Max WebSocket message size (default: 10MB)

### LLM Configuration

- Uses `claude-3-5-sonnet-20241022` by default
- All agent prompts in `app/prompts/`
- Temperature: 0.7 (creative but controlled)

### Channel Templates

Pre-built task sequences for:
- **LinkedIn**: Copy → Visual → Approval → Publish
- **Email**: Copy → HTML Build → QA/Test → Approval → Send
- **Instagram**: Visual → Copy → Approval → Publish
- **Paid Search**: Ad Copy → Audience → Bid Strategy → Approval → Launch

Extend in `app/utils/channel_templates.py`

## Project Structure

```
app/
├── main.py                 # FastAPI entry point
├── core/
│   ├── config.py          # Settings management
│   └── logging.py         # Structured logging
├── graph/
│   ├── state.py           # GraphState TypedDict
│   ├── builder.py         # Graph construction
│   ├── edges.py           # Conditional routing
│   └── nodes/             # Agent implementations
├── services/
│   ├── llm_service.py     # Claude integration
│   ├── slack_service.py   # Slack approval workflow
│   ├── analytics_service.py # GA4 + channel APIs
│   ├── websocket_manager.py # WebSocket connections
│   └── graph_runner.py    # Background execution
├── schemas/               # Pydantic models
├── prompts/               # Agent prompts
├── utils/                 # Helpers & templates
└── api/
    └── routes/            # API endpoints
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format
black app/

# Lint
ruff check app/
```

### Hot Reload

```bash
uvicorn app.main:app --reload --port 8000
```

## Deployment

### With Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -e .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment for Production

```bash
# .env.production
APP_ENV=production
LOG_LEVEL=INFO
ANTHROPIC_API_KEY=sk-...
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
BASE_URL=https://yourdomain.com
```

## Troubleshooting

### WebSocket Connection Fails
- Check CORS settings in `main.py`
- Ensure BASE_URL matches your ngrok tunnel
- Verify session_id in connection URL

### Slack Approval Not Sending
- Verify `SLACK_WEBHOOK_URL` is valid
- Check bot has permissions in your Slack workspace
- View logs for HTTP error responses

### LLM Errors
- Validate `ANTHROPIC_API_KEY` format
- Check token limits for long proposals
- Monitor rate limiting with exponential backoff

## Contributing

1. Fork and clone the repository
2. Create feature branch (`git checkout -b feature/your-feature`)
3. Add tests for new functionality
4. Ensure code passes linting and tests
5. Submit pull request with clear description

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or feedback:
- Check existing GitHub issues
- Open new issue with clear description
- Include logs from `app/core/logging.py`
