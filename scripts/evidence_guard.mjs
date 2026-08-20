#!/usr/bin/env node
/**
 * evidence_guard.mjs - PreToolUse 증거 무결성 보호(Write-Lock) 및 PostToolUse 해시 체크포인트 훅
 */

import fs from 'fs';
import path from 'path';
import crypto from 'crypto';

const hookType = process.argv[2] || 'pre-tool-use';

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

if (hookType === 'pre-tool-use') {
  // 1. PreToolUse: 원본 포렌식 증거 파일 쓰기 시도 차단
  const rawInput = process.env.ANTIGRAVITY_TOOL_INPUT || process.env.TOOL_INPUT || '';
  const protectedPatterns = [/\.raw$/i, /\.dmp$/i, /\.e01$/i, /\.evtx$/i, /\\evidence\\/i, /\/evidence\//i, /\$mft/i];

  for (const pattern of protectedPatterns) {
    if (pattern.test(rawInput)) {
      console.error(`[FORENSIC INTEGRITY GUARD] Write operation BLOCKED on protected forensic artifact matching: ${pattern}`);
      // 원본 증거 오염 방지를 위해 1 종료 코드 발생 (또는 에이전트 경고 주입)
      process.exit(1);
    }
  }
  process.exit(0);
} else if (hookType === 'post-tool-use') {
  // 2. PostToolUse: 산출물 생성 시 SHA-256 감사 로그 자동 기록
  const auditLogPath = path.resolve(process.cwd(), 'audit_trail.jsonl');
  const targetFile = process.env.ANTIGRAVITY_TARGET_FILE || process.env.TARGET_FILE;

  if (targetFile && fs.existsSync(targetFile)) {
    const hash = calculateSha256(targetFile);
    if (hash) {
      const entry = {
        timestamp: new Date().toISOString(),
        file: targetFile,
        sha256: hash,
        sizeBytes: fs.statSync(targetFile).size
      };
      fs.appendFileSync(auditLogPath, JSON.stringify(entry) + '\n', 'utf8');
    }
  }
  process.exit(0);
} else {
  process.exit(0);
}
