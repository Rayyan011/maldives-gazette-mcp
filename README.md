# Maldives Gazette MCP

A portable, **read-only Model Context Protocol server** for the official Maldives Government Gazette:

> https://www.gazette.gov.mv/gazette

It is agent-agnostic: every MCP-compatible client launches the same Python stdio server. No vendor SDK, account, cookie, API key, or hosted service is required.

## What it exposes

| Tool | Purpose |
|---|---|
| `gazette_status` | Check live reachability and HTTP status. |
| `gazette_categories` | List Law, Regulation, Decision, Procedure/Policy, Other, and Tax ruling categories. |
| `search_gazette` | Search by Unicode/Dhivehi keyword, category, volume, issue, date range, and page. |
| `get_gazette` | Read one record's title, volume, issue, publication date, and official PDF URL. |
| `browse_gazette` | Browse a public Gazette path such as `/gazette?page=2`. |
| `iulaan_categories` | List Iulaan categories, including tenders and job opportunities. |
| `search_iulaan` | Search public announcements by type, keyword, office, job category, date, and open status. |
| `get_iulaan` | Read one announcement's issuer, deadline, announcement number, and attachments. |

The server allowlists Gazette record pages and the official Google Storage PDF path. It never logs in, posts, edits, contacts anyone, or changes the source site.

## Install

Python 3.11+ is required.

```bash
git clone https://github.com/Rayyan011/maldives-gazette-mcp.git
cd maldives-gazette-mcp
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

The portable MCP command is:

```bash
/absolute/path/to/maldives-gazette-mcp/.venv/bin/python \
  /absolute/path/to/maldives-gazette-mcp/server.py
```

Use absolute paths in client configuration. Do not commit a machine-specific home directory into shared config.

## Verify

Run the real protocol test; it initializes an MCP client, discovers all eight tools, checks live status, searches a Gazette category, searches an open tender, searches an open government job, and reads detail pages:

```bash
.venv/bin/python tests/test_mcp_protocol.py
```

Manual stdio launch is also available:

```bash
.venv/bin/python server.py
```

## Client setup

All examples below use the same two values:

- `PYTHON`: `/absolute/path/to/maldives-gazette-mcp/.venv/bin/python`
- `SERVER`: `/absolute/path/to/maldives-gazette-mcp/server.py`

### Claude Code

```bash
claude mcp add maldives-gazette -- PYTHON SERVER
```

Or project `.mcp.json`:

```json
{
  "mcpServers": {
    "maldives-gazette": {
      "command": "/absolute/path/to/maldives-gazette-mcp/.venv/bin/python",
      "args": ["/absolute/path/to/maldives-gazette-mcp/server.py"]
    }
  }
}
```

### Codex CLI

```bash
codex mcp add maldives-gazette -- PYTHON SERVER
```

Or add the equivalent stdio server to Codex's MCP configuration using the JSON shape shown above.

### Cursor

Add this to Cursor's MCP settings or `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "maldives-gazette": {
      "command": "/absolute/path/to/maldives-gazette-mcp/.venv/bin/python",
      "args": ["/absolute/path/to/maldives-gazette-mcp/server.py"]
    }
  }
}
```

### Claude Desktop

Add the same `mcpServers` entry to Claude Desktop's `claude_desktop_config.json`.

### Gemini CLI

Register the same command as a local stdio MCP server in Gemini CLI's MCP settings. The server name should be `maldives-gazette`.

### Windsurf

Add the same JSON entry to Windsurf's MCP configuration (`mcp_config.json`).

### Cline / Roo Code

Use the MCP settings UI and add a stdio server:

- Name: `maldives-gazette`
- Command: `PYTHON`
- Arguments: `SERVER`

### VS Code MCP

Add the equivalent `mcp` server entry in the workspace or user MCP configuration, using the same `command` and `args`.

### Goose / Continue / other clients

Choose **stdio/local MCP server** and use:

```text
command: PYTHON
args: SERVER
```

The MCP protocol is the compatibility layer; no client-specific code is inside this repository.

### Hermes Agent

```bash
printf 'y\n' | hermes mcp add maldives-gazette \
  --command PYTHON \
  --connect-timeout 30 \
  --args SERVER
hermes mcp test maldives-gazette
```

## Usage examples

Search the latest regulations:

```text
Use search_gazette with category="gavaaidhu" and max_results=10.
```

Search by a record number or Dhivehi phrase:

```text
Use search_gazette with query="66-އާރ/2026".
```

Read one record:

```text
Use get_gazette with url_or_id="7539".
```

For legal or policy research, treat the linked official PDF as the authoritative document. A Gazette title alone does not establish current validity, repeal status, or legal effect.

## Included skills

The repository also includes portable, agent-agnostic skills under [`skills/`](skills/):

- [`gazette-business-project-finding`](skills/gazette/gazette-business-project-finding/SKILL.md) — discover, verify, and compare public tenders, bids, supplies, and project opportunities.
- [`gazette-government-job-finding`](skills/gazette/gazette-government-job-finding/SKILL.md) — find, verify, and compare government job announcements from Iulaan.

These are plain `SKILL.md` files and can be copied into Hermes, Claude Code, Codex, Cursor, or another agent's skill directory. They use the same MCP but remain separate workflows.

## Repository guidance

See [`AGENTS.md`](AGENTS.md) for setup, safety boundaries, testing requirements, and contribution rules.

## License

MIT
