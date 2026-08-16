---
name: ui-studio
description: 웹 뷰어·슬롭 제거·브랜드 토큰이 필요할 때만. 포렌식 수집·감정·법령·카카오 파싱에는 쓰지 말 것.
---

# ui-studio

UI 레인 게이트웨이. 포렌식 엔진이 아니다. 한 턴에 아래 참고 파일 **하나만** 읽는다.

| 요청 | 다음 파일 |
| :--- | :--- |
| 슬롭/AI 티 제거 | `../slopslap/REFERENCE.md` |
| 레이아웃/뷰어 | `../frontend-ui-ux/REFERENCE.md` |
| 브랜드 토큰 | `../design-system/REFERENCE.md` |

`frontend-ui-ux` 다음은 `mengto-skills/INDEX.md`에서 항목 **하나**.  
`design-system` 다음은 `design-systems/INDEX.md`에서 브랜드 **하나**.

`mengto-skills/**`, `design-systems/**`를 glob 하지 않는다. 구현은 `invoke_subagent` `Model: "flash"`.
