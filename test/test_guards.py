"""보안 핵심 훅(evidence_guard.mjs / hallucination_guard.mjs)의 회귀 테스트.

이 두 스크립트는 본 플러그인의 FAIL_CLOSED 보장을 담당하며 2026-08 리뷰까지
직접 테스트가 전무했다. 아래 테스트는 당시 발견된 결함들의 회귀를 고정한다:
- stdin 파이프 페이로드가 fstat().size==0 판정으로 버려지던 문제 (Linux/Windows)
- ASCII \\w 정규식이 한글 파일명을 놓치던 문제
- JSON 이스케이프(\\/)로 패턴을 회피하던 문제
- 콘텐츠 본문 언급만으로 쓰기가 차단되던 과차단
"""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NODE = "node"


def run_guard(script, argv=(), env=None, stdin_payload=None, cwd=None):
    e = os.environ.copy()
    if env:
        e.update(env)
    return subprocess.run(
        [NODE, str(ROOT / "scripts" / script), *argv],
        input=stdin_payload,
        text=True,
        encoding="utf-8",
        capture_output=True,
        env=e,
        cwd=str(cwd or ROOT),
    )


class EvidenceGuardTests(unittest.TestCase):
    def test_env_json_evidence_raw_is_blocked(self):
        proc = run_guard(
            "evidence_guard.mjs", ["pre-tool-use"],
            env={"TOOL_INPUT": json.dumps({"tool_input": {"file_path": "evidence/usb.raw"}})},
        )
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIn("BLOCKED", proc.stderr)

    def test_stdin_pipe_korean_dmp_is_blocked(self):
        # fstat.size==0 파이프 버그 회귀: stdin JSON 이 유일한 입력인 경로
        payload = json.dumps({"tool_input": {"file_path": "C:\\사건기록\\메모리덤프.dmp"}})
        proc = run_guard("evidence_guard.mjs", ["pre-tool-use"], stdin_payload=payload)
        self.assertEqual(proc.returncode, 1, proc.stderr)

    def test_json_escaped_evidence_path_is_blocked(self):
        proc = run_guard(
            "evidence_guard.mjs", ["pre-tool-use"],
            env={"TOOL_INPUT": '{"file_path": "C:\\\\/evidence\\\\/a.md"}'},
        )
        self.assertEqual(proc.returncode, 1, proc.stderr)

    def test_relative_cp_into_evidence_dir_is_blocked(self):
        proc = run_guard(
            "evidence_guard.mjs", ["pre-tool-use"],
            env={"TOOL_INPUT": json.dumps({"command": "cp img.dmp evidence/"})},
        )
        self.assertEqual(proc.returncode, 1)

    def test_report_content_mention_does_not_block(self):
        # 보고서 본문이 evidence/ 또는 image.raw 를 '언급'하는 것은 쓰기 차단 사유가 아니다
        proc = run_guard(
            "evidence_guard.mjs", ["pre-tool-use"],
            env={"TOOL_INPUT": json.dumps({
                "tool_input": {
                    "file_path": "out/보고서 초안.md",
                    "content": "증거는 evidence/usb.image 에서 확보했다. image.raw 라고도 부른다.",
                },
            })},
        )
        self.assertEqual(proc.returncode, 0)

    def test_unrelated_write_passes(self):
        proc = run_guard(
            "evidence_guard.mjs", ["pre-tool-use"],
            env={"TOOL_INPUT": json.dumps({"tool_input": {"file_path": "out/notes.md"}})},
        )
        self.assertEqual(proc.returncode, 0)

    def test_post_tool_use_writes_single_audit_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "보고서.md"
            report.write_text("# 감정서\n", encoding="utf-8")
            proc = run_guard(
                "evidence_guard.mjs", ["post-tool-use"],
                env={"TOOL_INPUT": json.dumps({"tool_input": {"file_path": str(report)}})},
                cwd=tmp,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            log = Path(tmp) / ".lazyforensic" / "audit_trail.jsonl"
            self.assertTrue(log.is_file())
            entry = json.loads(log.read_text(encoding="utf-8").strip().splitlines()[0])
            self.assertEqual(len(entry["sha256"]), 64)
            # 구버전이 만드는 이중 체인 로그(미러)는 없어야 한다
            self.assertFalse((Path(tmp) / "audit_trail.jsonl").exists())


class HallucinationGuardHookTests(unittest.TestCase):
    def test_korean_report_with_forbidden_phrase_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "감정서_보고서 초안.md"
            report.write_text("# 감정서\n\n명백히 입증되었다. 법원에 유효하다.\n", encoding="utf-8")
            proc = run_guard(
                "hallucination_guard.mjs", [],
                env={"TOOL_INPUT": json.dumps({"tool_input": {"file_path": str(report)}})},
                cwd=tmp,
            )
            self.assertEqual(proc.returncode, 1, proc.stderr)
            self.assertIn("FAIL", proc.stderr)

    def test_stdin_pipe_korean_report_is_gated(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "검토_보고서.md"
            report.write_text("# 보고서\n유출 확정이다.\n", encoding="utf-8")
            payload = json.dumps({"tool_input": {"file_path": str(report)}})
            proc = run_guard("hallucination_guard.mjs", [], stdin_payload=payload, cwd=tmp)
            self.assertEqual(proc.returncode, 1, proc.stderr)

    def test_fabricated_hash_blocked_with_audit_trail_grounding(self):
        with tempfile.TemporaryDirectory() as tmp:
            trail = Path(tmp) / ".lazyforensic" / "audit_trail.jsonl"
            trail.parent.mkdir()
            trail.write_text(json.dumps({"file": "x", "sha256": "a" * 64}) + "\n", encoding="utf-8")
            bad = Path(tmp) / "사건보고서.md"
            bad.write_text("# 보고서\n\nSHA-256: " + "c" * 64 + "\n", encoding="utf-8")
            proc = run_guard(
                "hallucination_guard.mjs", [],
                env={"TOOL_INPUT": json.dumps({"tool_input": {"file_path": str(bad)}})},
                cwd=tmp,
            )
            self.assertEqual(proc.returncode, 1, proc.stderr)
            self.assertIn("audit_trail.jsonl", proc.stderr)

    def test_grounded_report_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            trail = Path(tmp) / ".lazyforensic" / "audit_trail.jsonl"
            trail.parent.mkdir()
            h = "b" * 64
            trail.write_text(json.dumps({"file": "x", "sha256": h}) + "\n", encoding="utf-8")
            report = Path(tmp) / "감정보고서.md"
            report.write_text(f"# 감정서\n\nSHA-256: {h}\n비교 결과: 불부합\n", encoding="utf-8")
            proc = run_guard(
                "hallucination_guard.mjs", [],
                env={"TOOL_INPUT": json.dumps({"tool_input": {"file_path": str(report)}})},
                cwd=tmp,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_bash_redirect_write_is_gated(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "report_draft.md"
            report.write_text("x\n명백히 입증\n", encoding="utf-8")
            proc = run_guard(
                "hallucination_guard.mjs", [],
                env={"TOOL_INPUT": json.dumps({"command": f"python gen.py > {report}"})},
                cwd=tmp,
            )
            self.assertEqual(proc.returncode, 1, proc.stderr)

    def test_unrelated_note_is_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            note = Path(tmp) / "메모.md"
            note.write_text("그냥 메모\n", encoding="utf-8")
            proc = run_guard(
                "hallucination_guard.mjs", [],
                env={"TOOL_INPUT": json.dumps({"tool_input": {"file_path": str(note)}})},
                cwd=tmp,
            )
            self.assertEqual(proc.returncode, 0)

    def test_missing_target_is_skipped(self):
        proc = run_guard(
            "hallucination_guard.mjs", [],
            env={"TOOL_INPUT": json.dumps({"tool_input": {"file_path": "no/such/보고서.md"}})},
        )
        self.assertEqual(proc.returncode, 0)


if __name__ == "__main__":
    unittest.main()
