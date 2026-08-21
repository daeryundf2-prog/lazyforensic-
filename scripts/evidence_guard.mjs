#!/usr/bin/env node
/**
 * evidence_guard.mjs - PreToolUse 증거 무결성 보호(Write-Lock) 및 PostToolUse 해시 체크포인트 훅
 * Antigravity 호환: stdin JSON (tool_input) + 환경변수 모두 검사, best-effort 가드.
 * 실제 파일시스템 강제 잠금이 아니며, 증거 디렉토리는 OS 수준에서 읽기전용으로 두어야 한다.
 */

import fs from 'fs';
import path from 'path';
import crypto from 'crypto';

const hookType = (process.argv[2] || 'pre-tool-use').replace(/_/g, '-');

function calculateSha256(filePath) {
  try {
    const fileBuffer = fs.readFileSync(filePath);
    const hashSum = crypto.createHash('sha256');
    hashSum.update(fileBuffer);
    return hashSum.digest('hex');
  } catch (err) {
    return null;
  }
}

function readStdinSync() {
  try {
    // Antigravity는 hook에 stdin으로 JSON을 전달한다. 동기 읽기로 200ms 내 폴링.
    const fd = 0;
    const buf = Buffer.alloc(65536);
    // 비차단 읽기 시도 — TTY면 빈 문자열
    if (process.stdin.isTTY) return '';
    // stdin이 이미 닫혔거나 데이터가 없으면 빈 문자열
    let data = '';
    try {
      // Node 18+ fs.readFileSync(0) 는 stdin 전체를 읽는다 (데이터가 있을 때만 블록)
      // 타임아웃을 위해 짧게 시도: 이미 파이프된 데이터만 읽음
      const stat = fs.fstatSync(fd);
      if (stat.size === 0) {
        // 파이프 데이터가 없으면 환경변수로 폴백
        return '';
      }
      data = fs.readFileSync(fd, 'utf-8');
    } catch {
      return '';
    }
    return data;
  } catch {
    return '';
  }
}

function collectRawInput() {
  const parts = [];
  // 1) 환경변수 (레거시/테스트 호환)
  if (process.env.ANTIGRAVITY_TOOL_INPUT) parts.push(process.env.ANTIGRAVITY_TOOL_INPUT);
  if (process.env.TOOL_INPUT) parts.push(process.env.TOOL_INPUT);
  if (process.env.ANTIGRAVITY_TARGET_FILE) parts.push(process.env.ANTIGRAVITY_TARGET_FILE);
  if (process.env.TARGET_FILE) parts.push(process.env.TARGET_FILE);
  // 2) stdin JSON (Antigravity 실제 경로)
  const stdinRaw = readStdinSync();
  if (stdinRaw) parts.push(stdinRaw);
  // 3) CLI 인자로 전달된 JSON (일부 호스트)
  for (const arg of process.argv.slice(3)) parts.push(arg);
  return parts.join('\n');
}

if (hookType === 'pre-tool-use') {
  // 1. PreToolUse: 원본 포렌식 증거 파일 쓰기 시도 차단 (best-effort)
  const rawInput = collectRawInput();
  // 확장자 + 경로 패턴 + $MFT 변형 + 대용량 이미지 시그니처
  const protectedPatterns = [
    /\.raw$/im, /\.dd$/im, /\.dmp$/im, /\.e01$/im, /\.ex01$/im, /\.evtx$/im, /\.evtxc$/im,
    /\\evidence\\/i, /\/evidence\//i, /(^|\/|\\)evidence(\/|\\|$)/i,
    /\$mft/i, /\$logfile/i, /\$usnjrnl/i,
    /\/dev\/.*(sda|nvme|rdisk)/i,
  ];

  let blocked = null;
  for (const pattern of protectedPatterns) {
    if (pattern.test(rawInput)) {
      blocked = pattern;
      break;
    }
  }
  if (blocked) {
    console.error(`[FORENSIC INTEGRITY GUARD] Write operation BLOCKED on protected forensic artifact matching: ${blocked}`);
    console.error(`[HINT] Evidence files are read-only. Work on a copy in output/ or /tmp. This is a best-effort guard — also set OS read-only (chmod 444) on evidence/.`);
    // FAIL_CLOSED: 호스트가 exit 1을 차단 신호로 해석
    process.exit(1);
  }
  // 통과 시에도 감사 로그에 기록하지 않음
  process.exit(0);
} else if (hookType === 'post-tool-use') {
  // 2. PostToolUse: 산출물 생성 시 SHA-256 감사 로그 자동 기록
  const rawInput = collectRawInput();
  // 대상 파일 추정: 환경변수 > stdin JSON 내 file_path/target/output
  let targetFile = process.env.ANTIGRAVITY_TARGET_FILE || process.env.TARGET_FILE || '';
  if (!targetFile && rawInput) {
    try {
      const parsed = JSON.parse(rawInput);
      targetFile = parsed.tool_input?.file_path || parsed.tool_input?.target || parsed.tool_input?.output || parsed.file_path || '';
      if (!targetFile && typeof parsed === 'string') targetFile = parsed;
    } catch {
      // rawInput이 JSON이 아니면 경로 추출 시도
      const m = rawInput.match(/([\/\\][\w\-\.\/\\]+\.(html|json|csv|txt|png|mp4))/i);
      if (m) targetFile = m[1];
    }
  }

  // 감사 로그는 케이스 격리: .lazyforensic/audit_trail.jsonl 우선, 없으면 audit_trail.jsonl
  const auditDir = path.resolve(process.cwd(), '.lazyforensic');
  let auditLogPath = path.resolve(process.cwd(), 'audit_trail.jsonl');
  try {
    if (!fs.existsSync(auditDir)) fs.mkdirSync(auditDir, { recursive: true });
    auditLogPath = path.join(auditDir, 'audit_trail.jsonl');
  } catch {
    // mkdir 실패 시 cwd 폴백
  }

  if (targetFile && fs.existsSync(targetFile)) {
    try {
      const stat = fs.statSync(targetFile);
      // 2GB 이상은 해시 생략 (메모리 보호)
      if (stat.size > 2 * 1024 * 1024 * 1024) {
        process.exit(0);
      }
      const hash = calculateSha256(targetFile);
      if (hash) {
        const entry = {
          timestamp: new Date().toISOString(),
          file: path.resolve(targetFile),
          sha256: hash,
          sizeBytes: stat.size,
          hook: 'post-tool-use',
          note: 'best-effort SHA-256 checkpoint; not a chain-of-custody proof',
        };
        fs.appendFileSync(auditLogPath, JSON.stringify(entry) + '\n', 'utf8');
        // 레거시 경로에도 미러 (기존 테스트 호환)
        const legacyPath = path.resolve(process.cwd(), 'audit_trail.jsonl');
        if (legacyPath !== auditLogPath) {
          try { fs.appendFileSync(legacyPath, JSON.stringify(entry) + '\n', 'utf8'); } catch {}
        }
      }
    } catch {}
  }
  process.exit(0);
} else {
  process.exit(0);
}
