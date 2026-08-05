import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import * as cheerio from "cheerio";
import JSZip from "jszip";
import { PDFParse } from "pdf-parse";

const SITE = "https://www.gazette.gov.mv";
const GAZETTE = `${SITE}/gazette`;
const IULAAN = `${SITE}/iulaan`;
const MAX_BYTES = 8 * 1024 * 1024;

const TYPES: Record<string, string> = {
  "": "all", gavaaidhu: "Law", gaaoonu: "Regulation", qarar: "Decision",
  usool: "Procedure/Policy", "hisaab-thahugeebu": "Tax ruling", "noos-bayaan": "Press release",
  insurance: "Insurance", beelan: "Tender/Bid", vazeefaa: "Job opportunity",
  masakkaiy: "Work/Projects", "gannan-beynunvaa": "Supplies wanted",
  "kuyyah-dhinun": "Property for rent", "kuyyah-hifun": "Property wanted",
  neelan: "Auction", "aanmu-mauloomaathu": "General information", thamreenu: "Training",
};

const TRANSLATIONS: Record<string, string> = {
  admin: "އެޑްމިނިސްޓްރޭޓިވް", administrative: "އެޑްމިނިސްޓްރޭޓިވް",
  administration: "އެޑްމިނިސްޓްރޭޝަން", "software developer": "ސޮފްޓްވެއަރ ޑިވެލޮޕަރ",
  "software engineer": "ސޮފްޓްވެއަރ އިންޖިނިއަރ", "information technology": "އިންފޮމޭޝަން ޓެކްނޮލޮޖީ",
  "web developer": "ވެބް ޑިވެލޮޕަރ", "mobile developer": "މޯބައިލް ޑިވެލޮޕަރ",
  "data analyst": "ޑޭޓާ އެނަލިސްޓް", "cyber security": "ސައިބަރ ސެކިއުރިޓީ",
  "project manager": "ޕްރޮޖެކްޓް މެނޭޖަރ", construction: "ކޮންސްޓްރަކްޝަން",
  tender: "ބީލަން", job: "ވަޒީފާ", jobs: "ވަޒީފާ", developer: "ޑިވެލޮޕަރ",
  software: "ސޮފްޓްވެއަރ", technology: "ޓެކްނޮލޮޖީ", technical: "ޓެކްނިކަލް",
  engineer: "އިންޖިނިއަރ", system: "ސިސްޓަމް", systems: "ސިސްޓަމް",
  network: "ނެޓްވޯކް", database: "ޑޭޓާބޭސް", data: "ޑޭޓާ", analyst: "އެނަލިސްޓް",
  officer: "އޮފިސަރ", "human resources officer": "ހިއުމަން ރިސޯސަސް އޮފިސަރ", "hr officer": "ހިއުމަން ރިސޯސަސް އޮފިސަރ", "human resources": "ހިއުމަން ރިސޯސަސް",
 manager: "މެނޭޖަރ",
};

const text = (value: cheerio.Cheerio<any> | undefined) => value?.text().replace(/\s+/g, " ").trim() ?? "";
const absolute = (href: string) => new URL(href, SITE).toString();
const queryVariants = (query: string) => {
  const normalized = query.toLowerCase().trim().replace(/\s+/g, " ");
  if (!normalized || /[^\x00-\x7F]/.test(normalized)) return query ? [query] : [""];
  const out = [query];
  if (TRANSLATIONS[normalized]) out.push(TRANSLATIONS[normalized]);
  const translated = normalized.split(" ").map((x) => TRANSLATIONS[x] ?? x).join(" ");
  if (translated !== normalized) out.push(translated);
  normalized.split(" ").forEach((x) => { if (TRANSLATIONS[x]) out.push(TRANSLATIONS[x]); });
  return [...new Set(out)];
};

async function fetchBytes(url: string, maxBytes = MAX_BYTES) {
  const response = await fetch(url, { headers: { "User-Agent": "maldives-gazette-mcp/0.2" } });
  const buffer = Buffer.from(await response.arrayBuffer());
  if (buffer.byteLength > maxBytes) throw new Error(`response exceeds ${maxBytes} bytes`);
  return { response, buffer };
}
function safeSite(url: string) {
  const u = new URL(url); if (u.protocol !== "https:" || !["www.gazette.gov.mv", "gazette.gov.mv"].includes(u.hostname) || !(u.pathname.startsWith("/gazette") || u.pathname.startsWith("/iulaan"))) throw new Error("URL is outside the public Gazette allowlist"); return u.toString();
}
function safeAttachment(url: string) {
  const u = new URL(url);
  const officialStorage = u.hostname === "storage.googleapis.com" && u.pathname.startsWith("/gazette.gov.mv/docs/iulaan/");
  const officialCsc = ["www.csc.gov.mv", "csc.gov.mv"].includes(u.hostname) && u.pathname.startsWith("/download/");
  if (u.protocol !== "https:" || (!officialStorage && !officialCsc)) throw new Error("attachment is outside the official Gazette/CSC attachment allowlist");
  return u.toString();
}
function iulaanUrl(params: Record<string, string | number | boolean>) { const u = new URL(IULAAN); for (const [k,v] of Object.entries(params)) if (v !== "" && v !== false) u.searchParams.set(k, String(v)); return u.toString(); }

function parseGazette(html: string, source: string) {
  const $ = cheerio.load(html); const results: any[] = [];
  $(".items-list").each((_, el) => { const node=$(el); const a=node.find("a[href*='/gazette/']").first(); if(!a.length)return; const url=absolute(a.attr("href")!); results.push({ title:text(node.find(".gazette-title, h3, h2, h4").first())||text(a), url, category:text(node.find(".category").first())||null, published_date:text(node.find(".published-date, .date").first())||null, pdf_url:node.find("a[href$='.pdf']").first().attr("href")?absolute(node.find("a[href$='.pdf']").first().attr("href")!):null, source:url }); });
  if (!results.length) $("a[href^='/gazette/']").each((_,el)=>{const url=absolute($(el).attr("href")!); if(!results.some(x=>x.url===url)) results.push({title:text($(el)),url,source:url});});
  return {source, results:[...new Map(results.map(x=>[x.url,x])).values()]};
}
function parseIulaan(html: string, source: string) {
  const $=cheerio.load(html); const results:any[]=[];
  $(".items.bordered").each((_,el)=>{const n=$(el); const a=n.find("a.iulaan-title, a[href*='/iulaan/']").first(); if(!a.length)return; const url=absolute(a.attr("href")!); const info=n.find(".info").map((_,x)=>text($(x))).get(); results.push({title:text(n.find(".iulaan-title").first())||text(a),url,type:text(n.find(".iulaan-type").first())||null,office:text(n.find(".iulaan-office").first())||null,published_date:info.find((x:string)=>x.includes("ތާރީޚު"))?.replace(/^.*?ތާރީޚު:\s*/,"")||null,deadline:info.find((x:string)=>x.includes("ސުންގަޑި"))?.replace(/^.*?ސުންގަޑި:\s*/,"")||null,source:url});});
  return {source,total:results.length,results:[...new Map(results.map(x=>[x.url,x])).values()]};
}

const server = new Server({ name:"maldives-gazette", version:"0.2.0" }, { capabilities:{ tools:{} } });
server.setRequestHandler(ListToolsRequestSchema, async()=>({tools:[
  {name:"gazette_status",description:"Check public Gazette reachability.",inputSchema:{type:"object",properties:{}}},
  {name:"gazette_categories",description:"List Gazette categories.",inputSchema:{type:"object",properties:{}}},
  {name:"search_gazette",description:"Search public Gazette records.",inputSchema:{type:"object",properties:{query:{type:"string"},max_results:{type:"number"}}}},
  {name:"get_gazette",description:"Read one Gazette record.",inputSchema:{type:"object",properties:{url_or_id:{type:"string"},}}},
  {name:"browse_gazette",description:"Browse a public Gazette path.",inputSchema:{type:"object",properties:{path:{type:"string"},max_results:{type:"number"}}}},
  {name:"iulaan_categories",description:"List Iulaan categories.",inputSchema:{type:"object",properties:{}}},
  {name:"translate_iulaan_query",description:"Show standard Dhivehi Thaana query variants for an English phrase.",inputSchema:{type:"object",properties:{query:{type:"string"},},required:["query"]}},
  {name:"search_iulaan",description:"Search public Iulaan announcements; English queries are expanded into Dhivehi variants.",inputSchema:{type:"object",properties:{query:{type:"string"},announcement_type:{type:"string"},office:{type:"string"},job_category:{type:"string"},open_only:{type:"boolean"},page:{type:"number"},max_results:{type:"number"}}}},
  {name:"get_iulaan",description:"Read one Iulaan posting and its attachment links.",inputSchema:{type:"object",properties:{url_or_id:{type:"string"},},required:["url_or_id"]}},
  {name:"read_iulaan_attachment",description:"Extract text from an official Iulaan PDF or DOCX attachment.",inputSchema:{type:"object",properties:{url:{type:"string"},max_chars:{type:"number"}},required:["url"]}},
] }));

server.setRequestHandler(CallToolRequestSchema, async(req)=>{
  const name=req.params.name; const a=(req.params.arguments??{}) as Record<string,any>;
  try {
    if(name==="gazette_status"){const {response}=await fetchBytes(GAZETTE); return {content:[{type:"text",text:JSON.stringify({ok:response.ok,status:response.status,source:GAZETTE,checked_at:new Date().toISOString()})}]};}
    if(name==="gazette_categories") return {content:[{type:"text",text:JSON.stringify({source:GAZETTE,categories:Object.entries(TYPES).filter(([k])=>k).map(([type,label])=>({type,label,url:`${GAZETTE}?type=${type}`}))},null,2)}]};
    if(name==="translate_iulaan_query") return {content:[{type:"text",text:JSON.stringify({original_query:a.query,query_variants:queryVariants(a.query),translated_variants:queryVariants(a.query).slice(1)},null,2)}]};
    if(name==="iulaan_categories") return {content:[{type:"text",text:JSON.stringify({source:IULAAN,categories:Object.entries(TYPES).map(([type,label])=>({type,label,url:iulaanUrl({type})}))},null,2)}]};
    if(name==="search_iulaan"){
      const variants=queryVariants(a.query??""); const merged=new Map<string,any>(); let first="";
      for(const q of variants){const u=iulaanUrl({type:a.announcement_type??"",office:a.office??"", "job-category":a.job_category??"",q,"open-only":a.open_only??false,page:a.page>1?a.page:""}); if(!first)first=u; const {response,buffer}=await fetchBytes(u); const parsed=parseIulaan(buffer.toString("utf8"),u); parsed.results.forEach((r:any)=>{r.matched_query=q;merged.set(r.url,r);}); if(!response.ok)throw new Error(`HTTP ${response.status}`);}
      return {content:[{type:"text",text:JSON.stringify({url:first,total:merged.size,results:[...merged.values()].slice(0,Math.min(50,a.max_results??20)),status:200,query:a.query??"",query_variants:variants,announcement_type:TYPES[a.announcement_type??""]??a.announcement_type??"",requested_page:a.page??1,open_only:!!a.open_only,fetched_at:new Date().toISOString()},null,2)}]};
    }
    if(name==="search_gazette"||name==="browse_gazette") {const u=name==="browse_gazette"?safeSite(absolute(a.path??"/gazette")):GAZETTE; const {response,buffer}=await fetchBytes(u); const parsed=parseGazette(buffer.toString("utf8"),u); return {content:[{type:"text",text:JSON.stringify({...parsed,status:response.status,results:parsed.results.slice(0,Math.min(50,a.max_results??20)),fetched_at:new Date().toISOString()},null,2)}]};}
    if(name==="get_gazette"||name==="get_iulaan") {const base=name==="get_gazette"?GAZETTE:IULAAN; const u=safeSite(a.url_or_id?.startsWith("http")?a.url_or_id:`${base}/${a.url_or_id}`); const {response,buffer}=await fetchBytes(u); const $=cheerio.load(buffer.toString("utf8")); const attachments:any[]=[]; $("a[href]").each((_,el)=>{const h=$(el).attr("href")??""; if(/\.(pdf|docx?|xlsx?)$/i.test(h))attachments.push({label:text($(el)),url:absolute(h)});}); return {content:[{type:"text",text:JSON.stringify({url:u,status:response.status,title:text($(".iulaan-title, .gazette-title, h1, h2").first()),employer:text($(".office-name").first())||null,source:u,attachments,fetched_at:new Date().toISOString()},null,2)}]};}
    if(name==="read_iulaan_attachment"){const u=safeAttachment(a.url); const {response,buffer}=await fetchBytes(u); const ext=new URL(u).pathname.toLowerCase(); let extracted=""; if(ext.endsWith(".pdf")){const parsed = await new PDFParse({ data: buffer }).getText(); extracted = parsed.text;}else if(ext.endsWith(".docx")){const zip=await JSZip.loadAsync(buffer);const xml=await zip.file("word/document.xml")!.async("text");extracted=xml.replace(/<w:p[^>]*>/g,"\n").replace(/<[^>]+>/g,"").replace(/\s+/g," ").trim();}else throw new Error("supported attachment types: PDF and DOCX"); const max=Math.min(250000,Math.max(1000,a.max_chars??120000)); return {content:[{type:"text",text:JSON.stringify({url:u,status:response.status,characters:extracted.length,truncated:extracted.length>max,text:extracted.slice(0,max),source:u,fetched_at:new Date().toISOString()},null,2)}]};}
    throw new Error(`unknown tool: ${name}`);
  } catch(error){return {isError:true,content:[{type:"text",text:JSON.stringify({error:error instanceof Error?error.name:"Error",message:String(error),tool:name})}]};}
});

await server.connect(new StdioServerTransport());
