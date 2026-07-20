// Read-only dashboard over ../logs — run history per job + the latest brief.
// Deliberately no "run now" button: this can never trigger spend or actions.

import { serve } from "@hono/node-server";
import { Hono } from "hono";
import { readdir, readFile, stat } from "node:fs/promises";
import { join } from "node:path";

const LOGS_DIR = process.env.LOGS_DIR ?? "/logs";
const PORT = Number(process.env.PORT ?? 8787);
const RECENT_RUNS = 30;

interface HistoryEntry {
  ts: string;
  job: string;
  status: string;
  duration_s: number;
  cost_usd: number | null;
  num_turns: number | null;
  result: string;
  log: string;
}

const esc = (s: string) =>
  s.replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);

async function jobHistories(): Promise<Map<string, HistoryEntry[]>> {
  const jobs = new Map<string, HistoryEntry[]>();
  let dirs: string[] = [];
  try {
    dirs = (await readdir(LOGS_DIR, { withFileTypes: true }))
      .filter((d) => d.isDirectory())
      .map((d) => d.name);
  } catch {
    return jobs;
  }
  for (const dir of dirs.sort()) {
    try {
      const raw = await readFile(join(LOGS_DIR, dir, "history.jsonl"), "utf8");
      const entries = raw
        .trim()
        .split("\n")
        .filter(Boolean)
        .map((line) => JSON.parse(line) as HistoryEntry)
        .slice(-RECENT_RUNS)
        .reverse();
      jobs.set(dir, entries);
    } catch {
      // job dir without history yet — skip
    }
  }
  return jobs;
}

function jobTable(job: string, entries: HistoryEntry[]): string {
  const rows = entries
    .map(
      (e) => `<tr class="${e.status === "ok" ? "ok" : "fail"}">
        <td>${esc(e.ts)}</td>
        <td><span class="badge">${esc(e.status)}</span></td>
        <td>${e.duration_s}s</td>
        <td>${e.cost_usd != null ? `$${e.cost_usd.toFixed(3)}` : "—"}</td>
        <td>${e.num_turns ?? "—"}</td>
        <td class="result">${esc(e.result ?? "")}</td>
      </tr>`,
    )
    .join("\n");
  return `<section>
    <h2>${esc(job)}</h2>
    <table>
      <thead><tr><th>started</th><th>status</th><th>duration</th><th>cost</th><th>turns</th><th>result</th></tr></thead>
      <tbody>${rows || `<tr><td colspan="6">no runs yet</td></tr>`}</tbody>
    </table>
  </section>`;
}

const app = new Hono();

app.get("/", async (c) => {
  const jobs = await jobHistories();
  const hasBrief = await stat(join(LOGS_DIR, "morning_brief", "latest.html"))
    .then(() => true)
    .catch(() => false);
  const sections = [...jobs.entries()]
    .map(([job, entries]) => jobTable(job, entries))
    .join("\n");
  return c.html(`<!doctype html>
<html><head><meta charset="utf-8"><title>agent-jobs</title>
<style>
  body { font: 14px/1.5 -apple-system, system-ui, sans-serif; margin: 2rem auto; max-width: 960px; padding: 0 1rem; color: #2e2c27; }
  h1 { font-size: 1.3rem; } h2 { font-size: 1.05rem; margin-top: 2rem; }
  table { border-collapse: collapse; width: 100%; }
  th, td { text-align: left; padding: 6px 10px; border-bottom: 1px solid #e4e3dc; vertical-align: top; }
  th { color: #6b6a63; font-weight: 500; }
  .badge { padding: 1px 8px; border-radius: 4px; font-size: 12px; }
  tr.ok .badge { background: #e6f0e6; } tr.fail .badge { background: #f6e2da; }
  td.result { color: #6b6a63; max-width: 420px; overflow-wrap: anywhere; }
  a { color: #c6613f; }
</style></head>
<body>
  <h1>agent-jobs — run history</h1>
  ${hasBrief ? `<p><a href="/brief">Open the latest morning brief</a></p>` : ""}
  ${sections || "<p>No job logs found.</p>"}
</body></html>`);
});

app.get("/brief", async (c) => {
  try {
    const html = await readFile(
      join(LOGS_DIR, "morning_brief", "latest.html"),
      "utf8",
    );
    return c.html(html);
  } catch {
    return c.text("No brief rendered yet.", 404);
  }
});

serve({ fetch: app.fetch, port: PORT }, (info) => {
  console.log(`dashboard on http://localhost:${info.port} (logs: ${LOGS_DIR})`);
});
