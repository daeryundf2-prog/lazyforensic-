#!/usr/bin/env node
import { readdirSync, readFileSync, writeFileSync, existsSync } from "node:fs";
import { dirname, join, relative } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");

function frontmatterDescription(text) {
	if (!text.startsWith("---")) {
		return "";
	}
	const end = text.indexOf("\n---", 3);
	if (end < 0) {
		return "";
	}
	const block = text.slice(3, end);
	const match = block.match(/^description:\s*(.*)$/m);
	if (!match) {
		return "";
	}
	let value = match[1].trim();
	if (
		(value.startsWith('"') && value.endsWith('"')) ||
		(value.startsWith("'") && value.endsWith("'"))
	) {
		value = value.slice(1, -1);
	}
	return value.replace(/\s+/g, " ").trim();
}

function oneLine(text, limit = 80) {
	const clean = text.replace(/\|/g, "/").trim();
	if (clean.length <= limit) {
		return clean;
	}
	return `${clean.slice(0, limit - 1).trimEnd()}…`;
}

function collectSkills(dir, filename) {
	const rows = [];
	if (!existsSync(dir)) {
		return rows;
	}
	for (const category of readdirSync(dir, { withFileTypes: true })) {
		if (!category.isDirectory() || category.name.startsWith(".")) {
			continue;
		}
		const categoryDir = join(dir, category.name);
		for (const item of readdirSync(categoryDir, { withFileTypes: true })) {
			if (!item.isDirectory()) {
				continue;
			}
			const skillPath = join(categoryDir, item.name, filename);
			if (!existsSync(skillPath)) {
				continue;
			}
			const desc = frontmatterDescription(readFileSync(skillPath, "utf8"));
			rows.push({
				category: category.name,
				folder: item.name,
				need: oneLine(desc || item.name),
			});
		}
	}
	rows.sort((a, b) => {
		const cat = a.category.localeCompare(b.category);
		return cat !== 0 ? cat : a.folder.localeCompare(b.folder);
	});
	return rows;
}

function collectBrands(dir) {
	const rows = [];
	if (!existsSync(dir)) {
		return rows;
	}
	for (const item of readdirSync(dir, { withFileTypes: true })) {
		if (!item.isDirectory() || item.name.startsWith(".")) {
			continue;
		}
		const designPath = join(dir, item.name, "DESIGN.md");
		if (!existsSync(designPath)) {
			continue;
		}
		const desc = frontmatterDescription(readFileSync(designPath, "utf8"));
		rows.push({
			folder: item.name,
			need: oneLine(desc || item.name),
		});
	}
	rows.sort((a, b) => a.folder.localeCompare(b.folder));
	return rows;
}

function table(headers, rows) {
	const lines = [`| ${headers.join(" | ")} |`, `| ${headers.map(() => ":---").join(" | ")} |`];
	for (const row of rows) {
		lines.push(`| ${row.join(" | ")} |`);
	}
	return lines.join("\n");
}

function writeMengto() {
	const rows = collectSkills(join(root, "mengto-skills"), "SKILL.md");
	const groups = new Map();
	for (const row of rows) {
		if (!groups.has(row.category)) {
			groups.set(row.category, []);
		}
		groups.get(row.category).push(row);
	}
	const parts = [
		"# Meng To catalog",
		"",
		"Read **at most one** `mengto-skills/<category>/<name>/SKILL.md`. Do not glob this tree.",
		"",
		"UI kit only. Not a forensic collector.",
	];
	for (const [category, items] of groups) {
		parts.push("", `## ${category}`, "");
		parts.push(
			table(
				["Need", "Folder"],
				items.map((item) => [item.need, `\`${category}/${item.folder}\``]),
			),
		);
	}
	parts.push("");
	writeFileSync(join(root, "mengto-skills", "INDEX.md"), `${parts.join("\n")}\n`, "utf8");
	return rows.length;
}

function writeDesignSystems() {
	const rows = collectBrands(join(root, "design-systems"));
	const body = [
		"# Brand DESIGN.md catalog",
		"",
		"Read **at most one** `design-systems/<brand>/DESIGN.md`. Do not glob this tree.",
		"",
		"Tokens only. Trademark/reuse is not granted. Not a forensic engine.",
		"",
		table(
			["Need", "Brand folder"],
			rows.map((row) => [row.need, `\`${row.folder}\``]),
		),
		"",
	].join("\n");
	writeFileSync(join(root, "design-systems", "INDEX.md"), body, "utf8");
	return rows.length;
}

function writeAntv() {
	const body = [
		"# AntV Infographic catalog",
		"",
		"Read **at most one** file from this table. Do not glob `vendor/antv-infographic/`.",
		"",
		"Not a forensic collector. Do not invent sample evidence diagrams.",
		"",
		table(
			["Need", "File"],
			[
				["DSL 문법·템플릿 전체", "`creator-full.md`"],
				["노트 → Infographic DSL만", "`infographic-syntax-creator/SKILL.md`"],
				["구조(list/compare/sequence) 참고", "`infographic-structure-creator/SKILL.md`"],
				["항목 비주얼 참고", "`infographic-item-creator/SKILL.md`"],
				["템플릿 목록 갱신 참고", "`infographic-template-updater/SKILL.md`"],
			],
		),
		"",
	].join("\n");
	writeFileSync(join(root, "vendor", "antv-infographic", "INDEX.md"), body, "utf8");
}

const mengto = writeMengto();
const brands = writeDesignSystems();
writeAntv();
process.stdout.write(
	`wrote indexes: mengto=${mengto} design-systems=${brands} antv=5 from ${relative(process.cwd(), root) || "."}\n`,
);
