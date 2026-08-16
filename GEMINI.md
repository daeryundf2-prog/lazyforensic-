# LazyForensic — Gemini / Antigravity

호스트는 Google Antigravity, 기본 세션은 Gemini 3.7 Flash (High)다.
이 플러그인은 증거 자료를 정리하고 보고서 초안을 만든다. 포렌식 획득이나 법원 제출 적격성을 보장하지 않는다.

## 도구

| 목적 | 사용 |
| :--- | :--- |
| 파일·추출 프레임 읽기 | 호스트 `Read` (이미지 지원) |
| 파일 수정 | 호스트 `Write` / `Edit` |
| 탐색·파싱·초안·검증 | `invoke_subagent` |
| 법령 조회 | 빌드와 API 키를 확인한 `korean_law` MCP |

OpenCode `task(...)`, `model_tier`, `subagent_type`, Cursor `Task`, `view_file`을 만들지 않는다.

## `invoke_subagent` 계약

최상위 필드는 `Subagents`, `toolAction`, `toolSummary`다.
항목 필드는 `TypeName`, `Role`, `Model`, `Prompt`, `Workspace`다.
`Model`은 `inherit` | `flash_lite` | `flash` | `pro`만 허용한다.

```
invoke_subagent(
  Subagents=[{
    TypeName: "self",
    Role: "<short-role>",
    Model: "flash",
    Prompt: """
TASK: <명령형 작업>
DELIVERABLE: <정확한 산출물 또는 판정>
SCOPE: <경로와 제약>
VERIFY: <부모가 재실행할 검증>
ROLE ENVELOPE: mayFinalizeRun=false; mayModifyGlobalRunState=false; mustReturn=SubagentResultEnvelope; requiresParentAck=true
"""
  }],
  toolAction: "<역할> 서브에이전트 호출",
  toolSummary: "<한 줄 요약>"
)
```

레인 힌트는 `hostEnforced=false`다. `flash`는 파싱·초안, `pro`는 스크립트 출력과 주장 대조, `flash_lite`는 작은 작업에 쓴다.
세션 UI는 Gemini 3.7 Flash (High)를 유지한다. 호스트 `modelName`이 다르지 않으면 자식 모델이 바뀌었다고 말하지 않는다.

## 실패 폐쇄

- `--input`이 없으면 샘플 USB/카카오 유출 사건을 만들지 않는다.
- 파일·로그가 없으면 빈칸으로 둔다. 이벤트를 만들지 않는다.
- Windows 복사에서 생성시각 > 수정시각은 흔하다. Timestomping으로 단정하지 않는다.
- 카카오 파서는 텍스트 내보내기만 지원한다. SQLite를 읽지 않는다.
- 법령 MCP 빌드나 `LAW_OC`가 없으면 그 사실을 말하고 조문을 만들지 않는다.
- "명백히 입증", "법원에 유효"를 쓰지 않는다.
- 증거 오디오는 명시적 `--upload-audio` 동의 없이 외부로 보내지 않는다.

## 스킬 라우팅

아래에서 `SKILL.md` 하나만 읽는다.

| 요청 | 스킬 |
| :--- | :--- |
| 타임라인 HTML | `skills/forensic-timeline/SKILL.md` |
| 생성/수정 시각, 해시 | `skills/forensic-audit/SKILL.md` |
| 카카오톡 txt | `skills/kakao-chat-extractor/SKILL.md` |
| 감정서/보고서 초안 | `skills/forensic-report/SKILL.md` |
| CCTV/동영상 프레임 | `skills/forensic-video/SKILL.md` |
| 구간 자르기/필름스트립 | `skills/video-editor/SKILL.md` |
| 감정서 문장 교정 | `skills/korean-writing-reviewer/SKILL.md` |
| 계약 서식, 법령 조회 | `skills/legal-forensic-consult/SKILL.md` |
| DLP 표 정리 | `skills/dlp-leakage-detector/SKILL.md` |
| 인포그래픽 | `skills/infographic-creator/SKILL.md` |

UI 기능은 기본 스킬이 아니다. 사용자가 명시한 경우에만 다음 참고 파일을 읽는다.

- UI 슬롭: `skills/slopslap/REFERENCE.md`
- 웹 뷰어: `skills/frontend-ui-ux/REFERENCE.md`, 이후 `mengto-skills/INDEX.md`에서 하나
- 브랜드 토큰: `skills/design-system/REFERENCE.md`, 이후 `design-systems/INDEX.md`에서 하나

`mengto-skills/**`, `design-systems/**`를 glob 하지 않는다. 선택한 스킬이 지시하지 않으면 `vendor/`를 읽지 않는다.
전체 도구 형식은 `skills/references/antigravity-tools.md`에 있다.
