# Send Notification to Slack - Knative Function

A Knative function that receives CloudEvents and sends them to Slack. Built with FastAPI and uvicorn.

## Development Quick Start

### 1. Setup (with UV)

```bash
# Clone and setup
uv sync

# Optional: Configure Slack (function works without it)
cp .env.example .env
# Edit .env with your Slack webhook URL

# Run locally
uv run python func.py
```

### 2. Test

```bash
curl -X POST http://localhost:8080/ \
  -H "Content-Type: application/json" \
  -H "ce-specversion: 1.0" \
  -H "ce-type: com.example.test" \
  -H "ce-source: test/source" \
  -H "ce-id: 123" \
  -d '{"message": "Hello CloudEvents!"}'
```

### 3. Docker

```bash
# Build and run
docker build -t send-notification-to-slack .
docker run -p 8080:8080 send-notification-to-slack
```

## Configuration

### Slack Setup (Optional)

1. Create a Slack app at https://api.slack.com/apps
2. Enable "Incoming Webhooks" 
3. Set environment variables:

```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_CHANNEL=#your-channel
SLACK_DATA_LIMIT=256  # Character limit for event data
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SLACK_WEBHOOK_URL` | None | Slack webhook URL (optional) |
| `SLACK_CHANNEL` | None | Override webhook default channel |
| `SLACK_USERNAME` | "CloudEvent Bot" | Bot username |
| `SLACK_ICON_EMOJI` | ":cloud:" | Bot icon |
| `SLACK_DATA_LIMIT` | 256 | Max characters for event data |

## Endpoints

- `GET /health` - Health check
- `GET /ready` - Readiness check
- `POST /` - CloudEvent handler

## Knative Deployment

```bash
# Update func.yaml with your registry
func deploy
```

## Features

- Receives any CloudEvent type
- Optional Slack notifications with data truncation
- Health/readiness endpoints for Kubernetes
- Comprehensive logging
- Multi-platform Docker builds via GitHub Actions
