---
name: lazyforensic
description: 설명서·도움말·명령어와 포렌식·카카오톡 txt·타임라인·해시·감정서 라우터. 증거 없이 사건을 만들지 않는다.
---

# lazyforensic

Antigravity + Gemini 진입점. 먼저 `GEMINI.md`를 읽고, **레인 하나**만 고른 뒤 그 안에서 파일 **하나만** Read 한다.

## Help

사용자가 `설명서`, `도움말`, `명령어 알려줘`, `무엇을 할 수 있어?`라고 요청하면 `../../docs/USER_GUIDE.md`를 읽고 기능별 채팅 예시와 필요한 입력을 안내한다. 기능을 실행하지 않는다.

## Forensic

| 요청 | 스킬 |
| :--- | :--- |
| 타임라인 HTML | `../forensic-timeline/SKILL.md` |
| 생성/수정 시각, 해시 | `../forensic-audit/SKILL.md` |
| 카카오톡 내보내기 | `../kakao-chat-extractor/SKILL.md` |
| 감정서 초안 | `../forensic-report/SKILL.md` |
| CCTV/동영상 프레임 | `../forensic-video/SKILL.md` |
| 자르기/필름스트립 | `../video-editor/SKILL.md` |
| 문장 교정 | `../korean-writing-reviewer/SKILL.md` |
| DLP 표 | `../dlp-leakage-detector/SKILL.md` |

## Visual

| 요청 | 파일 |
| :--- | :--- |
| 인포그래픽 | `../infographic-creator/SKILL.md` |
| AntV 위성 | `../../vendor/antv-infographic/INDEX.md`에서 **하나** |
| Manim 참고 | `../video-editor`가 지시할 때만 `../video-editor/manim-video/REFERENCE.md` |

## Legal

계약 서식·법령 조회는 `../legal-forensic-consult/SKILL.md`. 세션의 `korean_law`가 `ready`일 때만 MCP를 쓴다. 조문을 만들지 않는다.

## UI

뷰어·슬롭·브랜드 토큰은 `../ui-studio/SKILL.md`로 넘긴다. 이 라우터에서 `mengto-skills/**`를 읽지 않는다.

병렬 작업은 `../references/antigravity-tools.md`의 `invoke_subagent`만 쓴다. `Model: "flash"` 초안, `Model: "pro"` 스크립트 출력 대조.
