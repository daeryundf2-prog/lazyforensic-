---
name: lazyforensic
description: 포렌식·카카오톡 txt·타임라인 HTML·해시·감정서 초안 라우터. 증거 없이 사건을 만들지 않는다. 일반 앱/웹 코딩에는 쓰지 말 것.
---

# lazyforensic

Antigravity + Gemini 진입점. 먼저 `GEMINI.md`를 읽고, 아래 표에서 **스킬 하나**만 Read 한다.

| 요청 | 스킬 |
| :--- | :--- |
| 타임라인 HTML | `../forensic-timeline/SKILL.md` |
| 생성/수정 시각, 해시 | `../forensic-audit/SKILL.md` |
| 카카오톡 내보내기 | `../kakao-chat-extractor/SKILL.md` |
| 감정서 초안 | `../forensic-report/SKILL.md` |
| CCTV/동영상 프레임 | `../forensic-video/SKILL.md` |
| 자르기/필름스트립 | `../video-editor/SKILL.md` |
| 문장 교정 | `../korean-writing-reviewer/SKILL.md` |
| 계약/법령 조회 | `../legal-forensic-consult/SKILL.md` |
| DLP 표 | `../dlp-leakage-detector/SKILL.md` |

병렬 작업은 `../references/antigravity-tools.md`의 `invoke_subagent`만 쓴다. `Model: "flash"` 초안, `Model: "pro"` 스크립트 출력 대조.

UI 기능은 포렌식 라우팅에서 제외한다. 사용자가 명시한 경우에만 `../slopslap/REFERENCE.md`, `../frontend-ui-ux/REFERENCE.md`, `../design-system/REFERENCE.md` 중 하나를 읽는다.
