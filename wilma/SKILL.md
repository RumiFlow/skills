---
name: wilma
description: Connect to the Wilma school system to retrieve messages, schedules, and homepage overview.
---

# Wilma School System Integration

This skill connects to the Finnish Wilma school system using the `wilma-python-sdk`.

## Capabilities

- **Homepage:** Get a quick overview of alerts and new items.
- **Messages:** Read inbox messages.
- **Schedule:** Check the daily school schedule.

## Usage

### Setup
The skill uses the shared virtual environment.

```bash
source /root/.venv/bin/activate
```

### Running the Server
```bash
python3 /root/.gemini/skills/wilma/scripts/wilma_mcp_server.py
```

## Configuration
Requires the shared `.env` file at `/root/.gemini/skills/.env`:

*   `WILMA_USER`: Username (email).
*   `WILMA_PASS`: Password.
*   `WILMA_URL`: URL of the Wilma server (e.g., `https://espoo.inschool.fi`).
*   `WILMA_APIKEY`: API Key (defaults to common open key).
