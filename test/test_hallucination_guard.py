import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN = ["명백히 입증", "법원에 유효", "유출 확정", "court-admissible", "Timestomping으로 단정"]


class HallucinationGuardTests(unittest.TestCase):
    def test_verify_report_blocks_forbidden(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "bad.md"
            report.write_text("명백히 입증 되었습니다. SHA256: " + "a"*64, encoding="utf-8")
            proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "verify_report.py"), str(report)], capture_output=True, text=True, cwd=str(ROOT))
            self.assertEqual(proc.returncode, 1)
            self.assertIn("명백히 입증", proc.stderr)

    def test_verify_report_blocks_orphan_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "hash.md"
            evidence = Path(tmp) / "evidence.json"
            report.write_text("해시: " + "b"*64, encoding="utf-8")
            evidence.write_text(json.dumps({"sha256": "a"*64}), encoding="utf-8")
            proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "verify_report.py"), str(report), "--evidence", str(evidence)], capture_output=True, text=True, cwd=str(ROOT))
            self.assertEqual(proc.returncode, 1)
            self.assertIn("근거 없는 해시", proc.stderr)

    def test_verify_report_passes_grounded(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "good.md"
            evidence = Path(tmp) / "evidence.json"
            h = "c"*64
            report.write_text(f"원본 SHA-256: {h}\n비교 결과: 미측정\n미확인", encoding="utf-8")
            evidence.write_text(h, encoding="utf-8")
            proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "verify_report.py"), str(report), "--evidence", str(evidence)], capture_output=True, text=True, cwd=str(ROOT))
            self.assertEqual(proc.returncode, 0)

    def test_no_skill_contains_forbidden_claim(self):
        for path in (ROOT / "skills").rglob("SKILL.md"):
            text = path.read_text(encoding="utf-8")
            for phrase in FORBIDDEN:
                if phrase in text:
                    idx = text.index(phrase)
                    ctx = text[max(0, idx-80):idx+80]
                    if any(k in ctx for k in ["쓰지 않는다", "금지", "FAIL", "의미가 아니다", "아니다", "하지 않는다"]):
                        continue
                    self.fail(f"{path} contains forbidden phrase '{phrase}' outside guard context: {ctx[:120]}")

    def test_gemini_has_hard_grounding(self):
        gemini = (ROOT / "GEMINI.md").read_text(encoding="utf-8")
        self.assertIn("근거-결론 분리", gemini)
        self.assertIn("미확인", gemini)
        self.assertIn("verify_report.py", gemini)
        self.assertIn("유출 확정", gemini)

    def test_forensic_report_skill_has_verify(self):
        skill = (ROOT / "skills" / "forensic-report" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("verify_report.py", skill)
        self.assertIn('Model: "pro"', skill)
        self.assertIn("미측정", skill)

    def test_timeline_and_kakao_still_fail_closed(self):
        # timeline without --input must be 2, kakao without file must be 2
        import importlib.util
        spec = importlib.util.spec_from_file_location("gt", str(ROOT / "skills" / "forensic-timeline" / "scripts" / "generate_timeline.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        self.assertEqual(m.main([]), 2)
        spec2 = importlib.util.spec_from_file_location("audit", str(ROOT / "skills" / "forensic-audit" / "scripts" / "audit_timestamps.py"))
        m2 = importlib.util.module_from_spec(spec2)
        spec2.loader.exec_module(m2)
        self.assertEqual(m2.main(["/no/such/file"]), 2)


if __name__ == "__main__":
    unittest.main()
