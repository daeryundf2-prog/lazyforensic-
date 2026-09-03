#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_report.py — 보고서 초안 할루시네이션 검증기
측정값 없이 채워진 결론, 금지 문구, 근거 없는 해시/시각을 차단한다.
Antigravity hard grounding: 부모가 Model pro로 재실행해야 하는 검증.

알려진 한계 (docs/GAPS.md):
- 해시 grounding 은 파일 단위 집합 비교다. 해시 A를 파일 B 서술에 붙이는
  '해시-파일 결합 오류'는 잡지 못한다.
- 법령 조문은 korean_law MCP 응답과의 자동 대조가 불가능하다. 출처 표기 없는
  조문 인용을 경고(WARN)로 알릴 뿐이다. 조문 텍스트 자체의 진위는 검증하지 않는다.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

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

# 금지 문구 직후에 이어지면 과단정이 아닌 부정/한정 문맥으로 보고 건너뛴다.
# 예: "유출의심 아님", "조작 가능성을 배제할 수 없다"
NEGATION_RE = re.compile(
    r"^\s*(?:을|를|이|가|은|는)?\s*"
    r"(?:아님|아니|않|없|불가|금지|못|불가능|배제|단정할 수 없|확인할 수 없|알 수 없)"
)


def scan_forbidden(text: str) -> list[str]:
    hits = []
    for phrase in FORBIDDEN_PHRASES:
        start = 0
        while True:
            idx = text.find(phrase, start)
            if idx == -1:
                break
            after = text[idx + len(phrase): idx + len(phrase) + 20]
            if not NEGATION_RE.match(after):
                hits.append(phrase)
                break
            start = idx + len(phrase)
    return hits


def extract_hashes(text: str) -> list[str]:
    """SHA-256 (64hex 전체) + 문맥 라벨이 붙은 MD5(32hex)/SHA-1(40hex).

    32/40 hex 는 무라벨 오탐이 많아 MD5/SHA-1 라벨이 같은 줄에 있을 때만 수집한다.

    줄바꿈·공백으로 분할된 64hex 도 잡는다(표 정렬·하드랩). 개행 결합은 두
    32hex 해시를 하나로 합쳐 환영 해시를 만들 수 있지만, 그 결과는 '근거 없는
    해시' 판정(실패폐쇄 방향)으로 귀결되므로 안전한 쪽의 오류다.
    """
    found = re.findall(r"\b[a-fA-F0-9]{64}\b", text)
    have = {h.lower() for h in found}
    for line in text.splitlines():
        if re.search(r"\bMD5\b|\bSHA-?1\b|md5_legacy", line, re.IGNORECASE):
            for pat in (r"\b[a-fA-F0-9]{40}\b", r"\b[a-fA-F0-9]{32}\b"):
                for h in re.findall(pat, line):
                    if h.lower() not in have:
                        found.append(h)
                        have.add(h.lower())
    # 분할 해시: 개행/공백이 hex 문자 사이에 낀 경우만 결합해 다시 찾는다.
    compact = re.sub(r"(?<=[a-fA-F0-9])[ \t]*\r?\n[ \t]*(?=[a-fA-F0-9])", "", text)
    if compact != text:
        for h in re.findall(r"\b[a-fA-F0-9]{64}\b", compact):
            if h.lower() not in have and h not in text:
                found.append(h)
                have.add(h.lower())
    return found


# 보고서/타임라인 양쪽에서 쓰는 날짜-시각 추출. 비교를 위해 정규형으로 통일한다.
ISO_DT_RE = re.compile(r"\b(\d{4})-(\d{1,2})-(\d{1,2})[ T](\d{1,2}):(\d{2})(?::(\d{2}))?\b")
ISO_DATE_RE = re.compile(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b")
# 한국식 표기: "2024년 5월 1일", "2024년 5월 1일 오전 9시 30분", "…오후 3시",
# "…9:30" — '시/분' 접미사와 오전/오후, 콜론식 시각을 모두 받는다.
# '시'만 있고 '분'이 없으면 정분(整分) 근거가 없으므로 00분으로 정규화한다.
KOR_DT_RE = re.compile(
    r"\b(?P<y>\d{4})년\s*(?P<mo>\d{1,2})월\s*(?P<d>\d{1,2})일\s*"
    r"(?:(?P<ampm>오전|오후)\s*)?"
    r"(?:"
    r"(?:(?P<hkor>\d{1,2})시)(?:\s*(?P<mikor>\d{1,2})분)?"
    r"|(?P<hiso>\d{1,2}):(?P<miiso>\d{2})(?::(?P<seiso>\d{2}))?"
    r")?"
)
DOT_DATE_RE = re.compile(r"\b(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})\.(?!\d)")


def _h12_to_24(ampm: str | None, hour: int | None) -> int | None:
    if hour is None:
        return None
    if ampm is None:
        return hour
    if ampm == "오후" and hour != 12:
        return hour + 12
    if ampm == "오전" and hour == 12:
        return 0
    return hour


def extract_timestamps(text: str) -> list[str]:
    """정규형 집합: 'YYYY-MM-DD HH:MM(:SS)' 와 'YYYY-MM-DD'."""
    out: set[str] = set()
    for m in ISO_DT_RE.finditer(text):
        y, mo, d, h, mi, s = m.groups()
        out.add(f"{int(y):04d}-{int(mo):02d}-{int(d):02d} {int(h):02d}:{mi}:{int(s) if s else 0:02d}")
    for m in KOR_DT_RE.finditer(text):
        date = f"{int(m.group('y')):04d}-{int(m.group('mo')):02d}-{int(m.group('d')):02d}"
        if m.group("hkor"):
            hour = int(m.group("hkor"))
            minute = int(m.group("mikor") or 0)
        elif m.group("hiso"):
            hour = int(m.group("hiso"))
            minute = int(m.group("miiso"))
        else:
            out.add(date)
            continue
        hour = _h12_to_24(m.group("ampm"), hour)
        out.add(f"{date} {hour:02d}:{minute:02d}:{0:02d}")
    for m in DOT_DATE_RE.finditer(text):
        y, mo, d = m.groups()
        out.add(f"{int(y):04d}-{int(mo):02d}-{int(d):02d}")
    for m in ISO_DATE_RE.finditer(text):
        y, mo, d = m.groups()
        out.add(f"{int(y):04d}-{int(mo):02d}-{int(d):02d}")
    return sorted(out)


# 법령 조문 인용: 제1016조, 제3조의2, 제3조 제2항 등. "제출/조치" 같은 일반 어휘와 구별.
LAW_CITATION_RE = re.compile(r"제\s*\d+\s*조(?:\s*의\s*\d+)?(?:\s*제?\s*\d+\s*항)?")
LAW_SOURCE_MARKER_RE = re.compile(r"korean_law|LawSearch|법제처|국가법령정보센터")


def read_text_smart(path: Path) -> tuple[str, str, bool]:
    """BOM/UTF-16/CP949를 순서대로 시도한다. 모두 실패하면 치환 문자로 읽고 lossy=True.

    구버전의 errors="ignore" 는 UTF-16 (Windows PowerShell Out-File 기본값) 입력을
    그대로 mojibake 로 만들어 금지 문구·해시 검출을 모두 놓쳤다.
    """
    raw = path.read_bytes()
    for enc in ("utf-8-sig", "utf-16", "cp949"):
        try:
            return raw.decode(enc), enc, False
        except (UnicodeDecodeError, UnicodeError):
            continue
    return raw.decode("utf-8", errors="replace"), "utf-8(lossy)", True


def load_evidence_hashes(evidence_paths: list[str]) -> set[str]:
    hashes: set[str] = set()
    for p in evidence_paths:
        path = Path(p)
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        hashes.update(h.lower() for h in extract_hashes(text))
        # json / jsonl 구조 필드 (sha256, md5, sha1)
        objs: list = []
        try:
            data = json.loads(text)
            objs.append(data)
        except Exception:
            for line in text.splitlines():
                try:
                    objs.append(json.loads(line))
                except Exception:
                    pass
        for obj in objs:
            items = obj if isinstance(obj, list) else [obj]
            for item in items:
                if isinstance(item, dict):
                    for key, val in item.items():
                        if isinstance(val, str) and re.match(r"^[a-fA-F0-9]{32,64}$", val):
                            hashes.add(val.lower())
    return hashes


EVIDENCE_TAG_RE = re.compile(r"<evidence>(.*?)</evidence>", re.DOTALL)
FABRICATED_AGENCY_RE = re.compile(
    r"\b(?:디지털포렌식청|사이버수사처|국가포렌식연구원|사이버범죄특별수사처|경찰청사이버보안국)\b"
)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Report hallucination guard — hard grounding verifier")
    parser.add_argument("report", help="Report draft path (.md/.html)")
    parser.add_argument("--evidence", nargs="*", default=[], help="Evidence files (audit json, audit_trail.jsonl, timeline json, etc.) for hash grounding")
    parser.add_argument("--timeline", help="Timeline events.json for timestamp grounding (optional)")
    parser.add_argument("--morph-grounding", action="store_true", help="Kiwi 형태소 기반 증거-보고서 용어 일치도 검증 (Section 5.2)")
    parser.add_argument("--json", action="store_true", help="Output JSON result")
    parser.add_argument("--strict", action="store_true", help="Fail with exit 1 if warnings are detected")
    args = parser.parse_args(argv)

    report_path = Path(args.report)
    if not report_path.exists():
        print(f"[-] Report not found: {report_path}", file=sys.stderr)
        return 2

    text, encoding_used, lossy = read_text_smart(report_path)

    errors = []
    warnings = []
    if lossy:
        warnings.append(f"보고서 인코딩 판별 실패({encoding_used}) — 치환 문자가 있어 검증 누락 가능")

    # 1) 금지 문구 (직후 부정 문맥은 제외)
    forbidden = scan_forbidden(text)
    if forbidden:
        errors.append(f"금지 문구 발견: {sorted(set(forbidden))} — GEMINI 실패폐쇄 위반")

    # 2) 해시 grounding (SHA-256 전체 + MD5/SHA-1 라벨 붙은 값)
    report_hashes = {h.lower() for h in extract_hashes(text)}
    if report_hashes:
        evidence_hashes = load_evidence_hashes(args.evidence)
        if evidence_hashes:
            orphan = report_hashes - evidence_hashes
            if orphan:
                errors.append(f"근거 없는 해시 {len(orphan)}개: {sorted(list(orphan))[:3]} — evidence 파일에 없는 해시를 보고서에 쓰지 말 것")
        elif args.evidence:
            errors.append(f"해시 {len(report_hashes)}개가 보고서에 있으나 evidence({args.evidence})에 해당 해시 없음 — audit_timestamps.py --json 결과 또는 .lazyforensic/audit_trail.jsonl 을 --evidence 로 전달해야 함")
        else:
            # --evidence 가 아예 없으면 grounding 근거 자체가 없다. 과거에는
            # WARN(통과)으로 두어 '감사 생략 + 조작 해시'라는 핵심 위협이
            # 게이트를 통과했다. 실패폐쇄: 근거 없는 해시는 어느 경로로
            # 들어왔든 FAIL이다.
            errors.append(
                f"근거 없는 해시 {len(report_hashes)}개: {sorted(list(report_hashes))[:3]} — "
                "--evidence 미제시로 grounding 불가. 감사 없이 쓴 해시는 조작과 구별할 수 없다. "
                "audit_timestamps.py <원본> --json > audit.json 후 --evidence 로 재검증할 것"
            )

    # 3) Chain of Custody 빈칸 검증: 해시 없음 + 결론이 '일치'이면 경고
    if "미측정" not in text and "미확인" not in text:
        if re.search(r"비교 결과[^\n]*일치", text) and not report_hashes:
            warnings.append("해시 없이 '일치' 결론 — '미측정'으로 표기해야 함")

    # 4) 타임라인 grounding (optional): 보고서 내 시각이 timeline에 있는지.
    #    미확인/미측정 표기가 '있는 줄'의 시각은 건너뛴다 (전역 치환 아닌 per-item 판정).
    if args.timeline:
        try:
            tl_text, _, _ = read_text_smart(Path(args.timeline))
            tl_times = set(extract_timestamps(tl_text))
            for line in text.splitlines():
                if "미확인" in line or "미측정" in line:
                    continue
                orphan_times = [t for t in extract_timestamps(line) if t not in tl_times]
                if orphan_times:
                    warnings.append(f"타임라인에 없는 시각 {orphan_times[:3]} — 근거 시각만 사용해야 함")
        except Exception:
            pass

    # 5) 법령 환각: 조문 인용이 있으면 korean_law MCP 출처 표기 요구 (자동 대조 불가 → WARN)
    citations = sorted(set(LAW_CITATION_RE.findall(text)))
    if citations and not LAW_SOURCE_MARKER_RE.search(text):
        preview = ", ".join(citations[:3]) + (f" 외 {len(citations) - 3}" if len(citations) > 3 else "")
        warnings.append(f"조문 인용({preview})이 있으나 korean_law MCP 출처 표기 없음 — MCP 응답과 대조 전까지 미확인으로 둘 것")

    # 5-1) 법령 조문 상한 경계 검사 (허위 조문 날조 FAIL 차단, 공백 유연성 및 중복 스팬 제거)
    STATUTE_BOUNDS = {
        "민법": 1118,
        "형법": 372,
        "개인정보보호법": 76,
        "정보통신망법": 76,
        "정보통신망 이용촉진 및 정보보호 등에 관한 법률": 76,
        "부정경쟁방지법": 18,
        "부정경쟁방지 및 영업비밀보호에 관한 법률": 18,
        "전자문서법": 37,
        "전자문서 및 전자거래 기본법": 37,
        "형사소송법": 493,
        "민사소송법": 502,
        "상법": 935,
        "행정소송법": 46,
        "근로기준법": 116,
        "특정금융정보법": 22,
        "특정 금융거래정보의 보고 및 이용 등에 관한 법률": 22,
        "전자상거래법": 45,
        "전자상거래 등에서의 소비자보호에 관한 법률": 45,
        "자본시장법": 449,
        "자본시장과 금융투자업에 관한 법률": 449,
        "신용정보법": 53,
        "신용정보의 이용 및 보호에 관한 법률": 53,
        "소비자기본법": 86,
        "가사소송법": 72,
        "특허법": 232,
        "저작권법": 142,
    }

    def _make_statute_pattern(statute_name: str) -> re.Pattern:
        clean_name = re.sub(r"\s+", "", statute_name)
        escaped_chars = [re.escape(c) for c in clean_name]
        pattern_str = r"\s*".join(escaped_chars) + r"\s*제\s*(\d+)\s*조(?:\s*의\s*(\d+))?"
        return re.compile(pattern_str)

    matched_spans: list[tuple[int, int]] = []
    sorted_statutes = sorted(STATUTE_BOUNDS.items(), key=lambda x: len(x[0]), reverse=True)

    for statute, max_art in sorted_statutes:
        pat = _make_statute_pattern(statute)
        for m in pat.finditer(text):
            span = m.span()
            if any(s <= span[0] and span[1] <= e for s, e in matched_spans):
                continue
            matched_spans.append(span)
            art_num = int(m.group(1))
            full_ref = m.group(0)
            if art_num > max_art or art_num < 1:
                errors.append(
                    f"{statute} 허위 조문 날조 발견: {full_ref} (현행 {statute}은 제1조~제{max_art}조까지만 존재함)"
                )

    # 5-2) 판례 연도 검사 (미래 연도 판결 날조 FAIL 차단)
    PRECEDENT_RE = re.compile(
        r"(?:대법원|서울고등법원|서울중앙지방법원|[가-힣]{2,6}지방법원|[가-힣]{2,6}고등법원|헌법재판소)?\s*"
        r"(?P<year>\d{4})\s*(?P<code>[가-힣]{1,4})\s*(?P<num>\d+)\b"
    )
    VALID_CASE_CODES = {
        # 민사
        "가단", "가합", "가소", "나", "다", "라", "마", "그", "바", "자", "차",
        # 보전처분 / 민사신청
        "카", "카단", "카합", "카기", "카담", "카조", "카열", "카경",
        # 형사
        "고단", "고합", "고약", "노", "도", "로", "모", "오", "보", "코",
        # 가사소송 및 가사비송
        "드", "드단", "드합", "르", "르단", "르합", "므", "스", "으",
        "느", "느단", "느합", "즈", "즈단", "즈합",
        # 도산 / 회생 / 파산
        "회단", "회합", "회개", "개회", "개단", "개합", "하단", "하합", "하면", "개확",
        # 행정 / 특허
        "구", "구합", "구단", "누", "두", "루", "무", "허",
        # 헌법재판소
        "헌가", "헌나", "헌다", "헌라", "헌마", "헌바", "헌사", "헌아",
        # 소년보호
        "푸", "버",
        # 재심
        "재가단", "재가합", "재다", "재나", "재도", "재노", "재고단", "재고합",
    }
    for m in PRECEDENT_RE.finditer(text):
        year = int(m.group("year"))
        code = m.group("code")
        num = m.group("num")
        case_str = f"{year}{code}{num}"
        if year > 2026:
            errors.append(
                f"판례 허위 날조 발견: 미래 연도 판결 인용 {case_str} (현재 2026년 이후 판결은 존재할 수 없음)"
            )
        elif year < 1948:
            errors.append(
                f"판례 허위 날조 발견: 대한민국 사법부 수립 이전 판결 {case_str} (1948년 이전)"
            )
        if code not in VALID_CASE_CODES:
            warnings.append(
                f"판례 부호 의심: 비표준 사건부호 인용 '{code}' in {case_str} — 대법원 규격 사건부호 여부를 확인하십시오."
            )

    # 5-3) 공공기관 및 수사기관 명칭 날조 검사 (Section 5.1 #2)
    for m in FABRICATED_AGENCY_RE.finditer(text):
        errors.append(f"공공기관 명칭 날조 발견: {m.group(0)} (Section 5.1 #2 실존하지 않는 수사/포렌식 기관)")

    # 5-4) <evidence> 태그 인용 검증 (Section 3.2 #1 Evidence-First)
    evidence_matches = EVIDENCE_TAG_RE.findall(text)
    if evidence_matches:
        combined_ev_text = ""
        for ep in args.evidence:
            p = Path(ep)
            if p.is_file():
                combined_ev_text += "\n" + p.read_text(encoding="utf-8", errors="replace")

        for quote in evidence_matches:
            q_strip = quote.strip()
            if not q_strip:
                errors.append("<evidence> 태그가 비어 있습니다. 증거 측정값을 채우십시오.")
            elif combined_ev_text:
                clean_q = re.sub(r"\s+", " ", q_strip)
                clean_ev = re.sub(r"\s+", " ", combined_ev_text)
                if clean_q not in clean_ev:
                    errors.append(
                        f"근거 인용 불일치: <evidence> 구절('{q_strip[:25]}...')이 제공된 증거 파일에 존재하지 않습니다."
                    )

    # 5-5) Kiwi 형태소 기반 포렌식 그라운딩 검증 (Section 5.2)
    if args.morph_grounding and args.evidence:
        try:
            from scripts.korean_morph_forensic import calculate_forensic_grounding
        except ImportError:
            try:
                from korean_morph_forensic import calculate_forensic_grounding
            except ImportError:
                calculate_forensic_grounding = None

        if calculate_forensic_grounding is not None:
            combined_ev = "\n".join(
                Path(ep).read_text(encoding="utf-8", errors="replace")
                for ep in args.evidence if Path(ep).is_file()
            )
            if combined_ev.strip():
                grounding_res = calculate_forensic_grounding(combined_ev, text, threshold=0.55)
                if not grounding_res["is_grounded"]:
                    warnings.append(
                        f"포렌식 형태소 그라운딩 미달 ({grounding_res['grounding_score']*100:.1f}% < 55%): "
                        f"증거에 없는 추정 용어 다수 {grounding_res['unsupported_terms'][:5]}"
                    )

    result = {
        "report": str(report_path),
        "encoding": encoding_used,
        "forbidden_hits": sorted(set(forbidden)),
        "report_hashes": sorted(list(report_hashes)),
        "law_citations": citations[:10],
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
            if args.strict:
                print(f"[FAIL] --strict 모드: 경고가 감지되어 차단합니다.", file=sys.stderr)
        else:
            print("[PASS] 할루시네이션 검증 통과 — 근거 없는 금지 문구/해시 없음")

    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
