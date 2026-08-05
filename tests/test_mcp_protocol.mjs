import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const transport = new StdioClientTransport({ command: process.execPath, args: ["dist/server.js"] });
const client = new Client({ name: "maldives-gazette-test", version: "0.2.0" });
await client.connect(transport);
const listed = await client.listTools();
const names = listed.tools.map((tool) => tool.name);
const expected = [
  "gazette_status", "gazette_categories", "gazette_filter_schema", "search_gazette", "search_gazette_advanced",
  "get_gazette", "get_gazette_print", "read_gazette_pdf", "search_gazette_pdf", "browse_gazette",
  "iulaan_categories", "iulaan_filter_schema", "translate_iulaan_query", "list_iulaan_offices", "search_iulaan",
  "search_iulaan_advanced", "browse_iulaan_pages", "get_iulaan", "get_iulaan_print", "list_iulaan_attachments",
  "read_iulaan_attachment", "search_iulaan_attachment_text",
];
for (const name of expected) if (!names.includes(name)) throw new Error(`missing tool: ${name}`);
const status = await client.callTool({ name: "gazette_status", arguments: {} });
const translation = await client.callTool({ name: "translate_iulaan_query", arguments: { query: "admin officer" } });
const search = await client.callTool({ name: "search_iulaan", arguments: { query: "admin officer", announcement_type: "vazeefaa", open_only: true, max_results: 5 } });
const iulaanSchema = await client.callTool({ name: "iulaan_filter_schema", arguments: {} });
const detail = await client.callTool({ name: "get_iulaan", arguments: { url_or_id: "405843" } });
for (const [label, result] of [["status", status], ["translation", translation], ["search", search], ["iulaanSchema", iulaanSchema], ["detail", detail]]) {
  if (result.isError) throw new Error(`${label} tool call failed: ${result.content?.[0]?.text ?? "unknown error"}`);
}
console.log(JSON.stringify({ tools: names, status, translation, search, iulaanSchema, detail }, null, 2));
await client.close();
