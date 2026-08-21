#!/usr/bin/env node
/**
 * hallucination_guard.mjs — PostToolUse 호스트 강제 할루시네이션 가드
 * "보고서" / "검토해줘" 가 포함된 모든 쓰기 후 무조건 실행.
 * LLM이 스킬을 스킵하고 직접 Write해도 호스트가 잡는다.
 */
import fs from 'fs';
import path from 'path';
import { spawnSync } from 'child_process';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');

function readStdinSync() {
  try {
    if (process.stdin.isTTY) return '';
    const stat = fs.fstatSync(0);
    if (stat.size === 0) return '';
    return fs.readFileSync(0, 'utf-8');
  } catch { return ''; }
}

function collectRawInput() {
  const parts = [];
  for (const k of ['ANTIGRAVITY_TOOL_INPUT','TOOL_INPUT','ANTIGRAVITY_TARGET_FILE','TARGET_FILE']) {
    if (process.env[k]) parts.push(process.env[k]);
  }
  const stdinRaw = readStdinSync();
  if (stdinRaw) parts.push(stdinRaw);
  for (const arg of process.argv.slice(2)) parts.push(arg);
  return parts.join('\n');
}

function shouldGuard(targetFile, rawInput) {
  // "보고서" / "검토" 키워드가 rawInput이나 파일명에 있으면 무조건 가드
  const keywordHit = /보고서|검토해줘|검증해줘|검증|할루시네이션|할루체크|팩트체크|거짓말검사|사실확인|무결성검사|verify|\/verify|\/할루체크|\/검증|법적.*검토/i.test(rawInput);
  const reportExt = /\.(md|html|txt)$/i.test(targetFile);
  const reportPathHint = /report|보고서|draft|초안/i.test(targetFile);
  // 키워드 + 보고서 파일이면 무조건, 그 외 보고서 파일은 샘플링(경량)
  if (keywordHit && reportExt) return true;
  if (reportPathHint && reportExt) return true;
  // DLP/보고서 외 일반 메모는 스킵 (오탐 방지) — 하지만 금지문구는 전역으로 잡기 위해 md/html이면 체크
  if (reportExt && fs.existsSync(targetFile)) {
    try {
      const text = fs.readFileSync(targetFile, 'utf-8');
      if (text.length > 500 && /(사건|감정|해시|SHA-256|증거)/.test(text)) return true;
    } catch {}
  }
  return false;
}

function extractTarget(rawInput) {
  let target = process.env.ANTIGRAVITY_TARGET_FILE || process.env.TARGET_FILE || '';
  if (!target && rawInput) {
    try {
      const parsed = JSON.parse(rawInput);
      target = parsed.tool_input?.file_path || parsed.tool_input?.target || parsed.tool_input?.output || parsed.file_path || parsed.output || '';
      if (!target && typeof parsed === 'string') target = parsed;
    } catch {
      const m = rawInput.match(/([\/\\][\w\-\.\/\\]+\.(?:md|html|txt|json))/i);
      if (m) target = m[1];
    }
  }
  // CLI 인자에서 경로 추출
  if (!target) {
    for (const arg of process.argv.slice(2)) {
      if (/\.(md|html|txt)$/.test(arg) && fs.existsSync(arg)) { target = arg; break; }
    }
  }
  return target;
}

const rawInput = collectRawInput();
const targetFile = extractTarget(rawInput);

if (!targetFile || !fs.existsSync(targetFile)) {
  // 가드 대상 파일 없으면 스킵 (오탐 방지)
  process.exit(0);
}

if (!shouldGuard(targetFile, rawInput)) {
  process.exit(0);
}

// 무조건 verify_report.py 실행 (호스트 강제)
const verifyScript = join(root, 'scripts', 'verify_report.py');
if (!fs.existsSync(verifyScript)) {
  process.exit(0);
}

// evidence 자동 탐색: 같은 디렉토리의 audit.json / events.json
const dir = path.dirname(path.resolve(targetFile));
const evidenceCandidates = [
  join(dir, 'audit.json'),
  join(process.cwd(), 'audit.json'),
  join(root, 'audit.json'),
].filter(p => fs.existsSync(p));

const args = [verifyScript, targetFile];
if (evidenceCandidates.length > 0) {
  args.push('--evidence', ...evidenceCandidates);
}

let res = spawnSync('python3', args, {
  cwd: root,
  encoding: 'utf-8',
  windowsHide: true,
});
if (res.error && res.error.code === 'ENOENT') {
  res = spawnSync('python', args, { cwd: root, encoding: 'utf-8', windowsHide: true });
}

if (res.status !== 0) {
  // FAIL: 금지문구/근거없는 해시 발견 → 호스트에 차단 신호
  const out = (res.stderr || res.stdout || '').toString();
  console.error(`[HALLUCINATION GUARD] 보고서 검증 FAIL — "${path.basename(targetFile)}" (호스트 강제, 보고서/검토해줘 트리거)`);
  console.error(out.slice(0, 1200));
  console.error(`[HINT] 금지문구(명백히 입증/법원에 유효/유출 확정) 제거, 해시는 audit.json 근거만 사용, 없으면 미확인/미측정으로 둬야 함. 수정 후 재시도.`);
  console.error(`[CMD] python scripts/verify_report.py "${targetFile}" --evidence audit.json --json`);
  // FAIL_CLOSED로 호스트가 후속 처리를 차단하도록 exit 1
  process.exit(1);
}

// PASS/WARN은 통과
if (res.stdout && res.stdout.includes('[WARN]')) {
  console.error(`[HALLUCINATION GUARD] WARN — ${path.basename(targetFile)}: ${res.stdout.slice(0, 600)}`);
}
process.exit(0);
