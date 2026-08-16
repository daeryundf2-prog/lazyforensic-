# LazyForensic — Gemini / Antigravity

Host: Google Antigravity. Session default: Gemini 3.7 Flash (High).
This plugin drafts DFIR artifacts. It is not a court-admissible suite.

## Tools

| Intent | Use |
| :--- | :--- |
| Read files / frames | host `Read` (images OK). Do not invent `view_file` |
| Edit files | host `Write` / `Edit` |
| Explore / parse / draft / verify | `invoke_subagent` only |
| Law lookup | `korean_law` MCP after `korean-law-mcp/build/index.js` exists |

Do not invent OpenCode `task(...)`, `model_tier`, `subagent_type`, or Cursor `Task`.

## `invoke_subagent`

Top-level: `Subagents`, `toolAction`, `toolSummary`.
Item: `TypeName`, `Role`, `Model`, `Prompt`, `Workspace`.
`Model`: `inherit` | `flash_lite` | `flash` | `pro`. No `model_tier`.

```
invoke_subagent(
  Subagents=[{
    TypeName: "self",
    Role: "<short-role>",
    Model: "flash",
    Prompt: """
TASK: <imperative>
DELIVERABLE: <artifact or verdict>
SCOPE: <paths>
VERIFY: <parent re-runs this>
ROLE ENVELOPE: mayFinalizeRun=false; mayModifyGlobalRunState=false; mustReturn=SubagentResultEnvelope; requiresParentAck=true
"""
  }],
  toolAction: "Invoking <role> subagent",
  toolSummary: "<one line>"
)
```

Lane hints (`hostEnforced=false`): `flash` parse/draft/UI, `pro` claim-check vs script output, `flash_lite` tiny chores.
Stay on Gemini 3.7 Flash (High) in the session UI. Do not claim the child model changed unless host `modelName` differs.

## Fail closed

- No `--input` → do not emit sample USB/Kakao leakage stories
- No file / no log → leave the cell empty. Do not invent events
- `os.stat` C>M is common on Windows copy. Not timestomping
- Kakao parser is text-export only. No SQLite
- Law MCP missing or no `LAW_OC` → say so. Do not fabricate statutes
- Do not write "명백히 입증" or "법원에 유효"

## Skill routing (Read one SKILL.md, not the vendor trees)

| User ask | Skill |
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
| UI 슬롭 | `skills/slopslap/SKILL.md` |
| 웹 뷰어 스타일 | `skills/frontend-ui-ux/SKILL.md` then at most one `mengto-skills/INDEX.md` pick |
| 브랜드 토큰 | `skills/design-system/SKILL.md` then at most one `design-systems/INDEX.md` pick |

Do not glob `mengto-skills/**` or `design-systems/**`. Do not load `vendor/` unless the chosen skill says so.

Full tool shape: `skills/references/antigravity-tools.md`.
