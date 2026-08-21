---
name: report-guard
description: 보고서/문서 할루시네이션 무조건 검증 — 금지문구/근거없는 해시 차단. Triggers: 보고서, 검토해줘, 검증해줘, 검증, 할루시네이션, 할루체크, 팩트체크, 거짓말검사, 사실확인, 무결성검사, verify
---

# report-guard: 무조건 검증 게이트

채팅에 아래 **어느 하나라도** 포함되면 호스트 `PostToolUse` + 이 스킬이 **무조건** `verify_report.py`를 실행한다. LLM이 스킵해도 호스트가 차단한다 (FAIL_CLOSED).

**트리거 (모두 동일 게이트)**:
`보고서`, `검토해줘`, `검증해줘`, `검증`, `할루시네이션`, `할루체크`, `팩트체크`, `거짓말검사`, `사실확인`, `무결성검사`, `verify`, `/verify`, `/할루체크`, `/검증`

## 동작

1. 대상 보고서(`.md`/`.html`)를 찾는다 — 가장 최근 `Write` 파일 또는 명시 경로
2. 아래를 무조건 검사:
   - 금지문구: `명백히 입증`, `법원에 유효`, `유출 확정`, `court-admissible`, `Timestomping으로 단정`
   - 해시 grounding: 보고서 내 64자 해시가 `--evidence` (audit.json/timeline.json) 에 없으면 FAIL
   - 빈칸 추측: `미확인/미측정`을 추측으로 채웠는지
3. `FAIL`이면 파일 유지하되 에러를 띄우고 **제출 금지**. `PASS/WARN`이면 통과 (WARN은 부모가 pro로 재대조)

## 실행 (스킬이 직접 하는 일 — 호스트도 동일하게 자동 실행)

```bash
# 스킬이 invoke_subagent Model: "pro"로 실행하는 검증
python scripts/verify_report.py "보고서초안.md" --evidence audit.json --timeline events.json --json
# 슬래시/채팅 어느 쪽이든 동일
python scripts/verify_report.py "보고서초안.md" --evidence audit.json --json
```

## Antigravity / Gemini

- 이 스킬 자체는 `Model: "pro"` 로 검증을 수행한다
- 동시에 호스트 `hallucination_guard.mjs`가 `PostToolUse`에서 동일 검증을 **자동 재실행**하므로 LLM이 이 스킬을 안 불러도 차단된다
- `보고서` 또는 `검토해줘`가 포함된 모든 쓰기는 이 게이트를 통과해야 한다 — `docs/GAPS.md` 위반 시 차단

## 슬래시 명령어

```
/verify <보고서경로> [--evidence audit.json]
/할루체크 <보고서경로>
/검증 <보고서경로>
검증해줘: <보고서경로>
보고서 검증해줘: <보고서경로>
팩트체크해줘: <보고서경로>
```

어느 형태로 불러도 동일 검증 (`verify_report.py`)이 돈다.
