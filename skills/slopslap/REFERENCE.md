# SlopSlap 선택 기능

포렌식 분석과 무관한 웹 UI 정리 기능이다. 사용자가 `/slopslap` 또는 UI 슬롭 제거를 명시한 경우에만 읽는다.

기본 실행은 `invoke_subagent` `Model: "flash"` **한 레인**으로 다음을 순차 점검한다.

1. 대표 슬롭
2. 레이아웃·컨테이너
3. 간격
4. 타이포
5. 색·대비

스캐너:

```bash
node skills/slopslap/scripts/scan-slop-signals.mjs <경로> --json
```

사용자가 정밀 병렬 점검을 명시한 경우에만 `FULL-WORKFLOW.md`를 읽어 5레인을 사용한다.
포렌식 턴에서는 호출하지 않는다.
