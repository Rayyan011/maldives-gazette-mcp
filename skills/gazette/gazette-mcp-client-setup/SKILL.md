---
name: gazette-mcp-client-setup
description: "Use when installing or configuring the Maldives Gazette MCP in an MCP client."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [maldives, gazette, mcp, typescript, setup]
    related_skills: []
---

# Gazette MCP Client Setup

Configure the TypeScript/Node.js stdio server for an MCP-compatible client.

## Standard setup

```bash
npm install
npm run build
node /absolute/path/to/maldives-gazette-mcp/dist/server.js
```

Use Node.js 20+ and absolute paths. The server is read-only and needs no credentials.

## Client configuration

Use this portable JSON shape:

```json
{
  "command": "/absolute/path/to/node",
  "args": ["/absolute/path/to/maldives-gazette-mcp/dist/server.js"]
}
```

For Claude Code or Codex CLI, use the client's stdio MCP add command with the same command and argument. For GUI clients, choose a local/stdio MCP server and enter the same values.

## Verification

Run `npm run test:protocol`. Confirm that all ten tools are listed and `gazette_status` returns the official site successfully. Never put credentials, cookies, or machine-specific secrets into the config.

## Pitfalls

- Build before configuring a client; clients launch `dist/server.js`, not `src/server.ts`.
- Use the Node executable path, not `npm`, as the MCP command.
- Keep diagnostics off stdout because stdout is the MCP transport.
- Rebuild after source changes.
