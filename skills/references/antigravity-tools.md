# Antigravity tool mapping (LazyForensic)

Defaults: Google Antigravity + Gemini 3.8 Flash (High).

## Do

| Intent | Action |
| --- | --- |
| Explore / parse / draft / QA / review | `invoke_subagent` with TASK / DELIVERABLE / SCOPE / VERIFY |
| Role envelope | `mayFinalizeRun=false`, `mayModifyGlobalRunState=false`, `mustReturn=SubagentResultEnvelope`, `requiresParentAck=true` |
| Child model hint (`canTierRoute`, not host-enforced) | `Subagents[].Model`: `flash` (parse/draft/UI), `pro` (verify claims vs script output), `flash_lite` (tiny chores), `inherit` |
| Read files / extracted frames | host `Read`; do not invent `view_file` |
| Edit | host `Write` / `Edit` |

## Canonical `invoke_subagent` shape

Live Antigravity schema: top-level `Subagents`, `toolAction`, `toolSummary`; item `TypeName`, `Role`, `Model`, `Prompt`, `Workspace`. `Model` enum: `inherit` | `flash_lite` | `flash` | `pro`. There is **no** `model_tier` field.

```
invoke_subagent(
  Subagents=[{
    TypeName: "self",
    Role: "<short-role>",
    Model: "flash",
    Prompt: """
TASK: <imperative assignment>
DELIVERABLE: <exact artifact or verdict>
SCOPE: <paths / constraints>
VERIFY: <commands or checks the parent will re-run>
ROLE ENVELOPE: mayFinalizeRun=false; mayModifyGlobalRunState=false; mustReturn=SubagentResultEnvelope; requiresParentAck=true
"""
  }],
  toolAction: "Invoking <role> subagent",
  toolSummary: "<one-line summary>"
)
```

`Workspace` is optional. Keep the session UI on Gemini 3.8 Flash (High). For verify lanes pass `Model: "pro"`. Passing `Model` is an agent hint (`hostEnforced=false`).

## Do not

- Foreign spawn/wait/goal APIs and OpenCode `task(...)` / `call_omo_agent(...)` / `team_*(...)`
- `subagent_type=` / `run_in_background=` / `load_skills=` / `model_tier=`
- Inventing evidence, statutes, or sample leakage timelines
