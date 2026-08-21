---
name: forensic-report
description: 포렌식 감정서/보고서 초안. 측정값만 채운다. 의뢰인 주장 입증·법원 적격 단정에는 쓰지 말 것.
---

# forensic-report: 보고서 초안 작성

분석 결과, 해시, 타임라인, 아티팩트 목록을 보고서 초안으로 정리한다.  
이 스킬은 감정인 서명, 법률 효력, 법원 채택을 보장하지 않는다.

## 목차

1. 사건 개요
2. 감정물 명세와 해시 (측정값만, 일치 단정은 값이 있을 때만)
3. 분석 환경과 도구 (실제 사용한 것만)
4. 쟁점별 관찰
5. 종합 — 데이터에 부합/불부합/판단 불능. 의뢰인 주장을 자동으로 입증하지 말 것.

## 품질 게이트

- [ ] Chain of Custody가 비어 있으면 빈칸으로 두고 채우지 말 것
- [ ] KST/UTC를 구분할 수 없으면 "미확인"으로 표기
- [ ] `$MFT`, Timestomping 등 용어는 실제 분석한 경우에만 사용
- [ ] "명백히 입증", "법원에 유효" 같은 선결론 금지

서식: `templates/forensic_report_template.md`. 초안은 `invoke_subagent` `Model: "flash"`, 선결론 점검은 `Model: "pro"`.

## Antigravity hard grounding (할루시네이션 차단)

모든 해시·시각·조문은 **측정 출력에만 근거**한다. 근거 없이 채우면 부모가 `verify_report.py`로 차단한다.

```bash
# 부모가 반드시 재실행하는 검증 (Model pro)
python skills/forensic-audit/scripts/audit_timestamps.py "증거파일" --json > audit.json  # 측정
python scripts/verify_report.py "보고서초안.md" --evidence audit.json --timeline events.json --json
# exit 1이면 금지문구/근거없는 해시 → 수정 없이 제출 금지
```

- 해시가 하나라도 있으면 `--evidence`로 audit/timeline을 넘겨야 함. 근거 없는 해시는 `FAIL`
- 금지문구(`명백히 입증`, `법원에 유효`, `유출 확정`, `Timestomping으로 단정`, `court-admissible`) 포함 시 `FAIL`
- Chain of Custody/시각이 없으면 `미측정`/`미확인`으로 둔다. 빈칸을 추측으로 채우지 않는다.
