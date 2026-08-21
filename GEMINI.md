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

## 실패 폐쇄 (할루시네이션 차단 — 최우선)

- `--input`이 없으면 샘플 USB/카카오 유출 사건을 만들지 않는다.
- 파일·로그가 없으면 빈칸 또는 `미확인`/`미측정`으로 둔다. 이벤트/해시/시각을 만들지 않는다.
- Windows 복사에서 생성시각 > 수정시각은 흔하다. Timestomping으로 단정하지 않는다.
- 카카오 파서는 텍스트 내보내기만 지원한다. SQLite를 읽지 않는다.
- 법령 MCP 빌드나 `LAW_OC`가 없으면 그 사실을 말하고 조문을 만들지 않는다.
- "명백히 입증", "법원에 유효", "유출 확정", "court-admissible", "Timestomping으로 단정"을 쓰지 않는다.
- 증거 오디오는 명시적 `--upload-audio` 동의 없이 외부로 보내지 않는다.
- **근거-결론 분리**: 모든 수치·해시·시각·조문은 스크립트 stdout / MCP 응답에만 근거한다. 근거 없으면 `미확인`으로 둔다. 추측으로 빈칸을 채우지 않는다.
- **부모 검증**: `forensic-report` 초안은 `Model: "pro"`가 `python scripts/verify_report.py <보고서> --evidence <audit.json>`로 재검증한다. `FAIL`이면 제출 금지.

## 스킬 라우팅

한 턴에 **레인 하나**만 고른다. 레인 안에서 `SKILL.md` / `REFERENCE.md` / `INDEX.md`를 **하나만** 읽는다.

> **무조건 검증**: 채팅에 `보고서`/`검토해줘`/`검증해줘`/`검증`/`할루시네이션`/`할루체크`/`팩트체크`/`거짓말검사`/`사실확인`/`무결성검사`/`verify` 중 하나라도 포함되면 호스트 `PostToolUse`가 `hallucination_guard.mjs → verify_report.py`를 **무조건** 실행한다. LLM이 스킬을 스킵하고 직접 `Write`해도 차단된다 (FAIL_CLOSED). 검증 FAIL이면 파일을 수정 없이 제출 금지. 슬래시 `/verify`, `/할루체크`, `/검증` 도 동일 게이트.

### Help

사용자가 `설명서`, `도움말`, `명령어 알려줘`, `무엇을 할 수 있어?`라고 하면 `docs/USER_GUIDE.md`를 읽고 기능별 요청 예시를 보여준다. 도움말 요청만으로 분석이나 파일 생성을 시작하지 않는다.

### Forensic (12+4+1 — BYO binary 래퍼는 도구 있을 때만, 보고서/검토해줘/검증 계열 = 무조건 검증)

진입점은 `skills/lazyforensic/SKILL.md`다. BYO 래퍼는 바이너리/라이브러리 미포함이며, 없으면 결과 생성 안 함.

| 요청 | 스킬 |
| :--- | :--- |
| 타임라인 HTML | `skills/forensic-timeline/SKILL.md` |
| 생성/수정 시각, 해시 | `skills/forensic-audit/SKILL.md` |
| 카카오톡 txt | `skills/kakao-chat-extractor/SKILL.md` |
| 감정서/보고서 초안 | `skills/forensic-report/SKILL.md` |
| **보고서 검증 (무조건)** | `skills/report-guard/SKILL.md` |
| CCTV/동영상 프레임 | `skills/forensic-video/SKILL.md` |
| 구간 자르기/필름스트립 | `skills/video-editor/SKILL.md` |
| 감정서 문장 교정 | `skills/korean-writing-reviewer/SKILL.md` |
| DLP 표 정리 | `skills/dlp-leakage-detector/SKILL.md` |
| EVTX 헌팅 (BYO Hayabusa/Chainsaw) | `skills/dfir-evtx-hunter/SKILL.md` |
| MFT/Prefetch (BYO Dissect/EZ-Tools) | `skills/forensic-mft-parser/SKILL.md` |
| 카카오 DB 래퍼 (txt만) | `skills/kakao-db-decryptor/SKILL.md` |
| 메모리 래퍼 (BYO MemProcFS) | `skills/memory-triage/SKILL.md` |

### Visual

| 요청 | 파일 |
| :--- | :--- |
| 인포그래픽 | `skills/infographic-creator/SKILL.md` |
| AntV 위성 | `vendor/antv-infographic/INDEX.md`에서 **하나** |
| Manim 참고 | `video-editor`가 지시할 때만 `skills/video-editor/manim-video/REFERENCE.md` |

### Legal

계약 서식·법령 조회는 `skills/legal-forensic-consult/SKILL.md`.  
세션 런타임의 `korean_law`가 `ready`일 때만 `korean_law` MCP를 쓴다. `missing-build`면 `node scripts/setup_korean_law.mjs`를 안내하고 조문을 만들지 않는다. `missing-LAW_OC`면 키 설정을 안내하고 조문을 만들지 않는다. 상세 API는 필요할 때만 `korean-law-mcp/docs/API.md` **한 파일**.

### UI

뷰어·슬롭·브랜드 토큰은 `skills/ui-studio/SKILL.md`만 피커에서 고른다. 그 스킬이 가리키는 REFERENCE **하나**, 이어서 INDEX에서 **하나**.

`mengto-skills/**`, `design-systems/**`를 glob 하지 않는다. 선택한 스킬이 지시하지 않으면 `vendor/`를 읽지 않는다.
전체 도구 형식은 `skills/references/antigravity-tools.md`에 있다.
