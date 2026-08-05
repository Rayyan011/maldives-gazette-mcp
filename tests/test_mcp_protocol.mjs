import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const transport = new StdioClientTransport({ command: process.execPath, args: ["dist/server.js"] });
const client = new Client({ name: "maldives-gazette-test", version: "0.2.0" });
await client.connect(transport);
const listed = await client.listTools();
const names = listed.tools.map((tool) => tool.name);
const expected = ["gazette_status", "gazette_categories", "search_gazette", "get_gazette", "browse_gazette", "iulaan_categories", "translate_iulaan_query", "search_iulaan", "get_iulaan", "read_iulaan_attachment"];
for (const name of expected) if (!names.includes(name)) throw new Error(`missing tool: ${name}`);
const status = await client.callTool({ name: "gazette_status", arguments: {} });
const translation = await client.callTool({ name: "translate_iulaan_query", arguments: { query: "admin officer" } });
const search = await client.callTool({ name: "search_iulaan", arguments: { query: "admin officer", announcement_type: "vazeefaa", open_only: true, max_results: 5 } });
console.log(JSON.stringify({ tools: names, status, translation, search }, null, 2));
await client.close();
