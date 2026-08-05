# Maldives Gazette MCP

A portable, **read-only Model Context Protocol server** for the official Maldives Government Gazette:

> https://www.gazette.gov.mv/gazette

It is agent-agnostic: every MCP-compatible client launches the same **TypeScript/Node.js stdio server**. No Python, virtualenv, account, cookie, API key, or hosted service is required.

## What it exposes

| Tool | Purpose |
|---|---|
| `gazette_status` | Check live reachability and HTTP status. |
| `latest_homepage_feed` | Read the newest Gazette and Iulaan cards shown on the official homepage. |
| `crawl_gazette_archive` / `crawl_iulaan_archive` | Crawl bounded archive pages with filters, deduplication, page counts, and stop reasons. |
| `research_domains` | List broad official research coverage. |
| `search_general_research` | Search Gazette and Iulaan together for broad public research. |
| `search_laws_regulations` | Search legal and policy Gazette categories together. |
| `search_public_notices` | Search general Iulaan notices and public-information records. |
| `gazette_categories` | List decoded Gazette categories and URL values. |
| `gazette_filter_schema` | Read the live Gazette form and its fields. |
| `search_gazette` / `search_gazette_advanced` | Search by category, volume, issue, query, date range, and page. |
| `get_gazette` | Read a record with structured ID, title, publication date, volume, issue, PDF, links, and visible text. |
| `get_gazette_print` | Read the Gazette detail page; the public site has no separate Gazette print route. |
| `read_gazette_pdf` | Extract text from an official Gazette PDF. |
| `search_gazette_pdf` | Search terms inside an official Gazette PDF. |
| `browse_gazette` | Browse a public Gazette path or page. |
| `iulaan_categories` | List decoded announcement and job-category values. |
| `iulaan_filter_schema` | Read the live Iulaan form and its fields. |
| `translate_iulaan_query` | Show standard Dhivehi Thaana query variants. |
| `list_iulaan_offices` | Discover public office/issuer filter links. |
| `search_iulaan` / `search_iulaan_advanced` | Search by announcement type, job category, office, query, dates, open status, and page. |
| `browse_iulaan_pages` | Browse a filtered Iulaan page with pagination. |
| `get_iulaan` | Read full posting text, employer, print URL, and attachments. |
| `get_iulaan_print` | Read the official Iulaan print view. |
| `list_iulaan_attachments` | List official TOR/application documents. |
| `read_iulaan_attachment` | Extract text from official PDF/DOCX attachments. |
| `search_iulaan_attachment_text` | Search terms inside an official attachment. |

The server allowlists Gazette record pages, official Gazette Storage attachments, and official CSC `/download/` attachments. It never logs in, posts, edits, contacts anyone, or changes the source site.

## Install

Node.js 20+ is required.

```bash
git clone https://github.com/Rayyan011/maldives-gazette-mcp.git
cd maldives-gazette-mcp
npm install
npm run build
```

The portable MCP command is:

```bash
node /absolute/path/to/maldives-gazette-mcp/dist/server.js
```


## Verify

Run the real Node MCP protocol test:

```bash
npm run test:protocol
```


## Client setup

All examples below use:

- `NODE`: `/absolute/path/to/node`
- `SERVER`: `/absolute/path/to/maldives-gazette-mcp/dist/server.js`

### Claude Code

```bash
claude mcp add maldives-gazette -- NODE SERVER
```

Or project `.mcp.json`:

```json
{
  "mcpServers": {
    "maldives-gazette": {
      "command": "/absolute/path/to/node",
      "args": ["/absolute/path/to/maldives-gazette-mcp/dist/server.js"]
    }
  }
}
```

### Codex CLI

```bash
codex mcp add maldives-gazette -- NODE SERVER
```

Or add the equivalent stdio server to Codex's MCP configuration using the JSON shape shown above.

### Cursor

Add this to Cursor's MCP settings or `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "maldives-gazette": {
      "command": "/absolute/path/to/node",
      "args": ["/absolute/path/to/maldives-gazette-mcp/dist/server.js"]
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
- Command: `NODE`
- Arguments: `SERVER`

### VS Code MCP

Add the equivalent `mcp` server entry in the workspace or user MCP configuration, using the same `command` and `args`.

### Goose / Continue / other clients

Choose **stdio/local MCP server** and use:

```text
command: NODE
args: SERVER
```

The MCP protocol is the compatibility layer; no client-specific code is inside this repository.

### Hermes Agent

```bash
printf 'y\n' | hermes mcp add maldives-gazette \
  --command NODE \
  --connect-timeout 30 \
  --args SERVER
hermes mcp test maldives-gazette
```

## Usage examples

Read the homepage's newest official records:

```text
Use latest_homepage_feed with source="all" and max_results=10.
```

Crawl a bounded archive safely:

```text
Use crawl_iulaan_archive with announcement_type="masakkaiy", from_page=1, max_pages=10, max_results=200.
```

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
- [`gazette-compensation-calculator`](skills/gazette/gazette-compensation-calculator/SKILL.md) — calculate transparent monthly salary estimates from fixed and attendance-based allowances.
- [`gazette-dhivehi-query-builder`](skills/gazette/gazette-dhivehi-query-builder/SKILL.md) — turn English research requests into standard Dhivehi Thaana search variants.
- [`gazette-job-shortlist-ranking`](skills/gazette/gazette-job-shortlist-ranking/SKILL.md) — rank job postings against a candidate's qualifications and preferences.
- [`gazette-deadline-monitor`](skills/gazette/gazette-deadline-monitor/SKILL.md) — re-check saved Iulaan postings and classify deadline risk.
- [`gazette-tor-evidence-extraction`](skills/gazette/gazette-tor-evidence-extraction/SKILL.md) — download and read official TORs and application documents, including English TORs.
- [`gazette-mcp-client-setup`](skills/gazette/gazette-mcp-client-setup/SKILL.md) — install and configure the TypeScript MCP in compatible clients.
- [`gazette-pdf-research`](skills/gazette/gazette-pdf-research/SKILL.md) — search and cite evidence inside official Gazette and Iulaan PDFs.
- [`gazette-filtered-search`](skills/gazette/gazette-filtered-search/SKILL.md) — use the website's live category, office, date, job, and open-status filters.

These are plain `SKILL.md` files and can be copied into Hermes, Claude Code, Codex, Cursor, or another agent's skill directory. They use the same MCP but remain separate workflows.

## Repository guidance

See [`AGENTS.md`](AGENTS.md) for setup, safety boundaries, testing requirements, and contribution rules.

## License

MIT
