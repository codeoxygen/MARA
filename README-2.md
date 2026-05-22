# MARA — Marketing Agentic Resource Assistant

> A multi-agent AI system that takes a marketing brief end-to-end: from campaign planning and human approval, through task assignment, to performance analytics — all streamed live via WebSocket.

---

## Table of Contents

- [Overview](#overview)
- [Agentic Workflow](#agentic-workflow)
- [Architecture](#architecture)
- [Folder Structure](#folder-structure)
- [Quick Start](#quick-start)
- [WebSocket Streaming](#websocket-streaming)
- [API Reference](#api-reference)
- [Agent Descriptions](#agent-descriptions)
- [Channel Task Templates](#channel-task-templates)
- [Environment Variables](#environment-variables)

---

## Overview

MARA automates the full marketing campaign lifecycle using a LangGraph-powered multi-agent pipeline. The system accepts a campaign brief, generates a structured campaign plan with channel-aware task breakdowns, routes it for human approval via email (with a revision loop), and finally produces a performance summary with recommended next actions.

The entire graph execution is streamed to the frontend via WebSocket, allowing real-time monitoring of each agent node as it runs.

---

## Agentic Workflow

```mermaid
flowchart TD
    START([User Submits Campaign Brief]) --> VALIDATE[Input Validator]
    VALIDATE -->|Invalid| ERR_INPUT([Return Validation Error])
    VALIDATE -->|Valid| BRIEF_ANALYST

    subgraph PLANNER_DOMAIN["🧠 Planner Domain"]
        BRIEF_ANALYST[Brief Analyst Agent\nParses intent, audience,\nchannel fit, inferred goals]
        CAMPAIGN_ARCHITECT[Campaign Architect Agent\nGenerates plan, phases,\nmessaging hierarchy]
        CHANNEL_EXPANDER[Channel Task Expander\nApplies per-channel\nproduction templates]
        TASK_ASSEMBLER[Task Assembler\nMerges all tasks,\nsets dependencies & owners]

        BRIEF_ANALYST -->|Enriched Brief| CAMPAIGN_ARCHITECT
        CAMPAIGN_ARCHITECT -->|Campaign Plan| CHANNEL_EXPANDER
        CHANNEL_EXPANDER -->|Expanded Task List| TASK_ASSEMBLER
    end

    subgraph LINKEDIN_TEMPLATE["📋 LinkedIn Task Template (per content piece)"]
        direction LR
        LI_COPY[Copy] --> LI_VISUAL[Visual] --> LI_APPROVAL[Approval] --> LI_PUBLISH[Publish]
    end

    CHANNEL_EXPANDER -.->|LinkedIn detected| LINKEDIN_TEMPLATE

    subgraph COMMS_DOMAIN["📨 Comms Domain"]
        PROPOSAL_FORMATTER[Proposal Formatter\nStructures plan into\nhuman-readable proposal]
        APPROVAL_HANDLER[Approval Handler\nSends email, polls response,\ninterprets feedback]
        REVISION_ROUTER{Response\nType?}

        PROPOSAL_FORMATTER --> APPROVAL_HANDLER
        APPROVAL_HANDLER --> REVISION_ROUTER
    end

    TASK_ASSEMBLER -->|Assembled Plan| PROPOSAL_FORMATTER

    REVISION_ROUTER -->|Changes Requested| REVISION_PARSER[Revision Parser\nExtracts actionable delta\nfrom human feedback]
    REVISION_PARSER --> CAMPAIGN_ARCHITECT

    REVISION_ROUTER -->|Rejected| PIPELINE_END_REJECT([Pipeline Terminated\nSummary Delivered])

    REVISION_ROUTER -->|Approved| PLAN_DELIVERED[Deliver Approved Plan\n& Task List to User]

    subgraph ANALYTICS_DOMAIN["📊 Analytics Domain"]
        METRICS_FETCHER[Metrics Fetcher\nGA4 + per-channel APIs\nrun in parallel]
        INSIGHTS_SYNTHESIZER[Insights Synthesizer\nCompares goals vs actuals,\ngenerates recommendations]

        METRICS_FETCHER -->|Normalized Metrics| INSIGHTS_SYNTHESIZER
    end

    PLAN_DELIVERED --> METRICS_FETCHER
    INSIGHTS_SYNTHESIZER --> FINAL_OUTPUT([Final Output\nPerformance Report\n+ Recommended Next Actions])

    style PLANNER_DOMAIN fill:#1e3a5f,stroke:#4a9eff,color:#fff
    style COMMS_DOMAIN fill:#3a1e5f,stroke:#a04aff,color:#fff
    style ANALYTICS_DOMAIN fill:#1e5f3a,stroke:#4aff9e,color:#fff
    style LINKEDIN_TEMPLATE fill:#5f3a1e,stroke:#ff9e4a,color:#fff
    style START fill:#4aff9e,color:#000
    style FINAL_OUTPUT fill:#4aff9e,color:#000
    style ERR_INPUT fill:#ff4a4a,color:#fff
    style PIPELINE_END_REJECT fill:#ff4a4a,color:#fff
```

---

## WebSocket Graph State Streaming

```mermaid
sequenceDiagram
    participant FE as Frontend
    participant API as FastAPI
    participant WS as WebSocket Manager
    participant BG as Background Thread
    participant LG as LangGraph

    FE->>API: POST /api/campaigns/run (brief payload)
    API->>BG: spawn_thread(graph.run, session_id)
    API-->>FE: 200 OK { session_id }
    FE->>WS: WS CONNECT /ws/{session_id}
    BG->>LG: graph.stream(state)
    loop Each Node Execution
        LG-->>BG: node_output event
        BG->>WS: broadcast(session_id, node_event)
        WS-->>FE: { node, status, payload, timestamp }
    end
    LG-->>BG: HITL interrupt (awaiting_approval)
    BG->>WS: broadcast(session_id, { node: "approval_handler", status: "waiting" })
    Note over FE,WS: Frontend shows "Awaiting human approval"
    BG-->>LG: resume(approval_response)
    LG-->>BG: graph complete
    BG->>WS: broadcast(session_id, { status: "complete", output: finalOutput })
    WS-->>FE: Final payload delivered
```

---

## Folder Structure

```
mara/
├── app/
│   ├── main.py                        # FastAPI app entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── campaigns.py           # POST /campaigns/run, GET /campaigns/{id}
│   │   │   └── websocket.py           # WS /ws/{session_id}
│   │   └── dependencies.py            # Shared FastAPI dependencies
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                  # Settings via pydantic-settings
│   │   └── logging.py                 # Structured logging setup
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── builder.py                 # LangGraph graph construction
│   │   ├── state.py                   # GraphState TypedDict
│   │   ├── edges.py                   # Conditional edge logic / routing
│   │   └── nodes/
│   │       ├── __init__.py
│   │       ├── input_validator.py
│   │       ├── brief_analyst.py
│   │       ├── campaign_architect.py
│   │       ├── channel_expander.py
│   │       ├── task_assembler.py
│   │       ├── proposal_formatter.py
│   │       ├── approval_handler.py
│   │       ├── revision_parser.py
│   │       ├── metrics_fetcher.py
│   │       └── insights_synthesizer.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py             # LLM client init, model selection
│   │   ├── email_service.py           # Gmail MCP / SMTP integration
│   │   ├── analytics_service.py       # GA4 API + channel metric clients
│   │   ├── websocket_manager.py       # Session WS connection registry
│   │   └── graph_runner.py            # Background thread runner + WS broadcaster
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── brief.py                   # CampaignBriefInput, EnrichedBrief
│   │   ├── campaign.py                # CampaignPlan, ContentPiece
│   │   ├── tasks.py                   # Task, TaskList, ChannelTaskGroup
│   │   ├── approval.py                # ApprovalRequest, ApprovalResponse
│   │   ├── analytics.py               # MetricsPayload, PerformanceReport
│   │   └── websocket.py               # WSEvent, WSNodeStatus
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── brief_analyst.py
│   │   ├── campaign_architect.py
│   │   ├── channel_expander.py
│   │   ├── proposal_formatter.py
│   │   ├── revision_parser.py
│   │   └── insights_synthesizer.py
│   └── utils/
│       ├── __init__.py
│       ├── channel_templates.py       # Channel → task template registry
│       └── state_helpers.py           # Graph state read/write helpers
├── .env.example
├── pyproject.toml
├── README.md
└── .gitignore
```

---

## Quick Start

```bash
# 1. Install dependencies
uv init & uv venv & uv source venv\bin\activate

# 2. Copy and fill environment variables
cp .env.example .env

# 3. Run the server
uvicorn app.main:app --reload --port 8000
```

---

## WebSocket Streaming

Connect to `ws://localhost:8000/ws/{session_id}` after receiving a `session_id` from the campaign run endpoint.

Each message is a JSON payload:

```json
{
  "session_id": "abc-123",
  "node": "brief_analyst",
  "status": "running | complete | error | waiting",
  "domain": "planner | comms | analytics",
  "payload": { },
  "iteration": 1,
  "timestamp": "2025-05-22T10:00:00Z"
}
```

---

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/campaigns/run` | Submit brief, start graph, return `session_id` |
| `GET` | `/api/campaigns/{session_id}` | Get current graph state snapshot |
| `POST` | `/api/campaigns/{session_id}/resume` | Inject approval response to resume HITL |
| `WS` | `/ws/{session_id}` | Stream real-time node events |

---

## Agent Descriptions

| Agent | Domain | Responsibility |
|-------|--------|---------------|
| Input Validator | Pre-graph | Schema validation of raw brief |
| Brief Analyst | Planner | Enriches brief with inferred goals, flags gaps |
| Campaign Architect | Planner | Generates campaign phases, messaging, content plan |
| Channel Expander | Planner | Expands each content piece into channel-specific task templates |
| Task Assembler | Planner | Merges all tasks, sets dependencies and suggested owners |
| Proposal Formatter | Comms | Formats plan into structured, readable proposal |
| Approval Handler | Comms | Sends email, polls response, interprets and routes feedback |
| Revision Parser | Comms | Extracts structured revision delta from free-text feedback |
| Metrics Fetcher | Analytics | Parallel fetch from GA4 and channel APIs |
| Insights Synthesizer | Analytics | Compares goals vs actuals, produces recommendations |

---

## Channel Task Templates

| Channel | Task Sequence |
|---------|--------------|
| LinkedIn | Copy → Visual → Approval → Publish |
| Email | Copy → HTML Build → QA/Test → Approval → Send |
| Instagram | Visual → Copy → Approval → Publish |
| Paid Search | Ad Copy → Audience Setup → Bid Strategy → Approval → Launch |

---

## Environment Variables

```env
# LLM
ANTHROPIC_API_KEY=

# Email
GMAIL_MCP_SERVER_URL=
APPROVAL_EMAIL_RECIPIENT=

# Analytics
GA4_PROPERTY_ID=
GOOGLE_APPLICATION_CREDENTIALS=

# App
APP_ENV=development
LOG_LEVEL=INFO
MAX_REVISION_ITERATIONS=5
```
