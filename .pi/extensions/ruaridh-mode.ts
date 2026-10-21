import { existsSync, readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const EXTREMELY_IMPORTANT_MARKER = "<EXTREMELY_IMPORTANT>";
const BOOTSTRAP_MARKER = "ruaridh-mode bootstrap";

const extensionDir = dirname(fileURLToPath(import.meta.url));
const packageRoot = resolve(extensionDir, "../..");
const skillsDir = resolve(packageRoot, ".claude/skills");
const skillDir = resolve(skillsDir, "ruaridh-mode");
const referencesDir = resolve(skillDir, "references");
const fullBodyPath = resolve(skillDir, "SKILL.md");
const slimBodyPath = resolve(referencesDir, "slim.md");
const linkedSkillsPath = resolve(packageRoot, "linked-skills.txt");

const bootstrapCache = new Map<string, string>();

export default function ruaridhModePiExtension(pi: ExtensionAPI) {
	let injectBootstrap = true;

	pi.on("resources_discover", async () => ({
		skillPaths: linkedSkillPaths(),
	}));

	pi.on("session_start", async () => {
		injectBootstrap = true;
	});

	pi.on("session_compact", async () => {
		injectBootstrap = true;
	});

	pi.on("agent_end", async () => {
		injectBootstrap = false;
	});

	pi.on("context", async (event) => {
		if (!injectBootstrap) return;
		if (event.messages.some(messageContainsBootstrap)) return;

		const bootstrap = getBootstrapContent();
		if (!bootstrap) return;

		const bootstrapMessage = {
			role: "user" as const,
			content: [{ type: "text" as const, text: bootstrap }],
			timestamp: Date.now(),
		};

		const insertAt = firstNonCompactionSummaryIndex(event.messages);
		return {
			messages: [
				...event.messages.slice(0, insertAt),
				bootstrapMessage,
				...event.messages.slice(insertAt),
			],
		};
	});
}

function linkedSkillNames(): string[] {
	let raw: string;
	try {
		raw = readFileSync(linkedSkillsPath, "utf8");
	} catch {
		return [];
	}
	return raw
		.split("\n")
		.map((line) => line.split("#", 1)[0].trim())
		.filter((name) => name.length > 0);
}

function linkedSkillPaths(): string[] {
	const paths = linkedSkillNames()
		.map((name) => resolve(skillsDir, name))
		.filter((path) => existsSync(path));
	if (paths.length > 0) return paths;
	return existsSync(skillDir) ? [skillDir] : [];
}

function getBootstrapContent(): string | null {
	const worker = process.env.RUARIDH_MODE === "worker";
	const cacheKey = worker ? "slim" : "full";
	const cached = bootstrapCache.get(cacheKey);
	if (cached !== undefined) return cached;

	const bodyPath = worker ? slimBodyPath : fullBodyPath;
	let body: string;
	try {
		body = stripFrontmatter(readFileSync(bodyPath, "utf8"));
	} catch {
		body = `Could not read the ruaridh-mode skill at ${bodyPath}. Continue without it.`;
	}

	const bootstrap = `${EXTREMELY_IMPORTANT_MARKER}
${BOOTSTRAP_MARKER}

The ruaridh-mode skill is already loaded below; follow it and do not load it again. Its references are under ${referencesDir}.

${body}

${piToolMapping()}
</EXTREMELY_IMPORTANT>`;

	bootstrapCache.set(cacheKey, bootstrap);
	return bootstrap;
}

function stripFrontmatter(content: string): string {
	const match = content.match(/^---\n[\s\S]*?\n---\n([\s\S]*)$/);
	return (match ? match[1] : content).trim();
}

function piToolMapping(): string {
	return `## Pi tool mapping

Pi has native skills but does not expose Claude Code's \`Skill\` tool. When ruaridh-mode says to invoke a skill, use Pi's native skill system instead: load the relevant \`SKILL.md\` with \`read\` when the skill applies, or let a human invoke \`/skill:name\` explicitly.

Pi's built-in coding tools are lowercase: \`read\`, \`write\`, \`edit\`, \`bash\`, plus optional \`grep\`, \`find\`, and \`ls\`. Use those for the corresponding actions: read a file, create or edit files, run shell commands, search file contents, find files by name, and list directories.

Pi does not ship a subagent tool such as Claude Code's \`Task\`. Spawn a Herdr pane instead, following the \`herdr\` skill: a sibling or child agent gets its own tab or pane, a brief, and a two-file handoff. Never invent \`Task\` calls.

Pi does not ship a standard task-list tool. If an installed todo/task tool is available, use it. Otherwise track work in plan files or a repo-local \`TODO.md\` when task tracking is needed. Treat older \`TodoWrite\` references as this task-tracking action.`;
}

function messageContainsBootstrap(message: unknown): boolean {
	const content = (message as { content?: unknown }).content;
	if (typeof content === "string") return content.includes(BOOTSTRAP_MARKER);
	if (!Array.isArray(content)) return false;
	return content.some((part) => {
		return (
			part &&
			typeof part === "object" &&
			(part as { type?: unknown }).type === "text" &&
			typeof (part as { text?: unknown }).text === "string" &&
			(part as { text: string }).text.includes(BOOTSTRAP_MARKER)
		);
	});
}

function firstNonCompactionSummaryIndex(messages: unknown[]): number {
	let index = 0;
	while ((messages[index] as { role?: unknown } | undefined)?.role === "compactionSummary") {
		index += 1;
	}
	return index;
}
