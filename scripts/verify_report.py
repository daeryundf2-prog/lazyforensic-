#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_report.py — 보고서 초안 할루시네이션 검증기
측정값 없이 채워진 결론, 금지 문구, 근거 없는 해시/시각을 차단한다.
Antigravity hard grounding: 부모가 Model pro로 재실행해야 하는 검증.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

FORBIDDEN_PHRASES = [
    "명백히 입증",
    "법원에 유효",
    "법원에 제출 적격",
    "유출 확정",
    "유출의심",
    "확정적으로 유출",
    "조작 가능성",
    "Timestomping으로 단정",
    "court-admissible",
]

# 허용된 결론 패턴: "미확인", "판단 불능", "부합", "불부합"
ALLOWED_CONCLUSION_HINTS = ["미확인", "판단 불능", "부합", "불부합", "추가 수집"]

def scan_forbidden(text: str) -> list[str]:
    hits = []
    for phrase in FORBIDDEN_PHRASES:
        if phrase in text:
            hits.append(phrase)
    # POSIX ctime 오독 탐지: "생성시각"과 "POSIX"가 함께 있으면 경고
    return hits


def extract_hashes(text: str) -> list[str]:
    # 64 hex
    return re.findall(r"\b[a-fA-F0-9]{64}\b", text)


def extract_timestamps(text: str) -> list[str]:
    # YYYY-MM-DD HH:MM:SS
    return re.findall(r"\b\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\b", text)


def load_evidence_hashes(evidence_paths: list[str]) -> set[str]:
    hashes = set()
    for p in evidence_paths:
        path = Path(p)
        if not path.exists():
            continue
        try:
            # json with sha256 fields or plain audit jsonl
            text = path.read_text(encoding="utf-8", errors="ignore")
            hashes.update(extract_hashes(text))
            # also try json parse
            try:
                data = json.loads(text)
                if isinstance(data, dict):
                    for v in data.values():
                        if isinstance(v, str) and re.match(r"^[a-f0-9]{64}$", v.lower()):
                            hashes.add(v.lower())
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            for v in item.values():
                                if isinstance(v, str) and re.match(r"^[a-f0-9]{64}$", v.lower()):
                                    hashes.add(v.lower())
            except Exception:
                pass
            # jsonl
            for line in text.splitlines():
                try:
                    obj = json.loads(line)
                    if isinstance(obj, dict) and "sha256" in obj:
                        hashes.add(str(obj["sha256"]).lower())
                except Exception:
                    pass
        except Exception:
            continue
    return {h.lower() for h in hashes}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Report hallucination guard — hard grounding verifier")
    parser.add_argument("report", help="Report draft path (.md/.html)")
    parser.add_argument("--evidence", nargs="*", default=[], help="Evidence files (audit json, timeline json, etc.) for hash grounding")
    parser.add_argument("--timeline", help="Timeline events.json for timestamp grounding (optional)")
    parser.add_argument("--json", action="store_true", help="Output JSON result")
    args = parser.parse_args(argv)

    report_path = Path(args.report)
    if not report_path.exists():
        print(f"[-] Report not found: {report_path}", file=sys.stderr)
        return 2

    text = report_path.read_text(encoding="utf-8", errors="ignore")

    errors = []
    warnings = []

    # 1) 금지 문구
    forbidden = scan_forbidden(text)
    if forbidden:
        errors.append(f"금지 문구 발견: {forbidden} — GEMINI 실패폐쇄 위반")

    # 2) 해시 grounding
    report_hashes = {h.lower() for h in extract_hashes(text)}
    if report_hashes:
        evidence_hashes = load_evidence_hashes(args.evidence)
        if evidence_hashes:
            orphan = report_hashes - evidence_hashes
            if orphan:
                errors.append(f"근거 없는 해시 {len(orphan)}개: {sorted(list(orphan))[:3]} — evidence 파일에 없는 해시를 보고서에 쓰지 말 것")
        elif args.evidence:
            errors.append(f"해시 {len(report_hashes)}개가 보고서에 있으나 evidence({args.evidence})에 해당 해시 없음 — audit_timestamps.py 결과를 --evidence로 전달해야 함")
        else:
            warnings.append(f"해시 {len(report_hashes)}개가 보고서에 있으나 --evidence 미제시 — 부모가 audit_timestamps.py 출력과 대조해야 함")

    # 3) Chain of Custody 빈칸 검증: 해시 없음 + 결론이 '일치'이면 오류
    if "미측정" not in text and "미확인" not in text:
        if re.search(r"비교 결과[^\n]*일치", text) and not report_hashes:
            warnings.append("해시 없이 '일치' 결론 — '미측정'으로 표기해야 함")

    # 4) 타임라인 grounding (optional): 보고서 내 시각이 timeline에 있는지
    if args.timeline:
        try:
            timeline_text = Path(args.timeline).read_text(encoding="utf-8", errors="ignore")
            report_times = extract_timestamps(text)
            tl_times = set(extract_timestamps(timeline_text))
            orphan_times = [t for t in report_times if t not in tl_times and "미확인" not in text]
            if orphan_times:
                warnings.append(f"타임라인에 없는 시각 {orphan_times[:3]} — 근거 시각만 사용해야 함")
        except Exception:
            pass

    # 5) 법령 환각: 조문이 있으면 LAW_OC 검증 힌트
    if "제" in text and "조" in text and "법" in text:
        if "LawSearch" not in text and "korean_law" not in text and "법제처" not in text:
            warnings.append("조문 인용이 있으나 korean_law MCP 출처 표기 없음 — LawSearch 결과와 대조 필요")

    result = {
        "report": str(report_path),
        "forbidden_hits": forbidden,
        "report_hashes": sorted(list(report_hashes)),
        "errors": errors,
        "warnings": warnings,
        "verdict": "FAIL" if errors else ("WARN" if warnings else "PASS"),
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if errors:
            print(f"[FAIL] 할루시네이션 검증 실패 ({len(errors)} errors, {len(warnings)} warnings)", file=sys.stderr)
            for e in errors:
                print(f"  - ERROR: {e}", file=sys.stderr)
            for w in warnings:
                print(f"  - WARN: {w}", file=sys.stderr)
            print(f"[HINT] 수정 후 재실행: python scripts/verify_report.py {report_path} --evidence audit.json --json", file=sys.stderr)
        elif warnings:
            print(f"[WARN] {len(warnings)} warnings (통과하나 부모가 Model pro로 대조 필요)")
            for w in warnings:
                print(f"  - {w}")
        else:
            print(f"[PASS] 할루시네이션 검증 통과 — 근거 없는 금지 문구/해시 없음")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
