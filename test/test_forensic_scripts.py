import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def load_module(name, relpath):
    path = ROOT / relpath
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(relpath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


timeline = load_module("generate_timeline", "skills/forensic-timeline/scripts/generate_timeline.py")
audit = load_module("audit_timestamps", "skills/forensic-audit/scripts/audit_timestamps.py")
kakao = load_module("parse_kakao", "skills/kakao-chat-extractor/scripts/parse_kakao.py")
video_config = load_module("forensic_video_config", "skills/forensic-video/scripts/config.py")
video_whisper = load_module("forensic_video_whisper", "skills/forensic-video/scripts/whisper.py")


class TimelineTests(unittest.TestCase):
    def test_missing_input_exits_nonzero(self):
        # given no --input
        # when CLI runs
        code = timeline.main([])
        # then argparse fails closed
        self.assertEqual(code, 2)

    def test_empty_events_ok(self):
        # given empty list
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "empty.json"
            out = Path(tmp) / "out.html"
            src.write_text("[]", encoding="utf-8")
            # when
            code = timeline.main(["--input", str(src), "--output", str(out)])
            # then
            self.assertEqual(code, 0)
            html = out.read_text(encoding="utf-8")
            self.assertIn("0 건", html)
            self.assertNotIn("SanDisk", html)

    def test_escapes_html(self):
        # given XSS payload events
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out.html"
            # when
            code = timeline.main([
                "--input", str(FIXTURES / "events_xss.json"),
                "--output", str(out),
            ])
            # then
            self.assertEqual(code, 0)
            html = out.read_text(encoding="utf-8")
            self.assertNotIn("<script>alert(1)</script>", html)
            self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)
            self.assertIn("&lt;img src=x onerror=alert(1)&gt;", html)
            self.assertIn("a &amp; b", html)

    def test_rejects_object_root(self):
        # given object instead of list
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "bad.json"
            out = Path(tmp) / "out.html"
            src.write_text('{"timestamp":"x"}', encoding="utf-8")
            # when
            code = timeline.main(["--input", str(src), "--output", str(out)])
            # then
            self.assertEqual(code, 2)
            self.assertFalse(out.exists())

    def test_iso_events_are_sorted_and_critical_label_is_neutral(self):
        # given reverse-ordered ISO events
        events = [
            {"timestamp": "2024-01-16 15:00:00", "category": "critical", "description": "later"},
            {"timestamp": "2024-01-16 14:00:00", "category": "system", "description": "earlier"},
        ]
        # when
        html = timeline.generate_html(events)
        # then
        self.assertLess(html.index("earlier"), html.index("later"))
        self.assertIn("시각 오름차순", html)
        self.assertIn(">주의<", html)
        self.assertNotIn("유출의심", html)

    def test_source_has_no_sample_usb_story(self):
        # given generator source
        src = (ROOT / "skills/forensic-timeline/scripts/generate_timeline.py").read_text(encoding="utf-8")
        # then no baked leakage narrative
        self.assertNotIn("SanDisk", src)
        self.assertNotIn("최종_설계안.zip", src)


class AuditTests(unittest.TestCase):
    def test_missing_file_exits_nonzero(self):
        # given missing path
        code = audit.main([str(ROOT / "no-such-file-for-audit.bin")])
        # then
        self.assertEqual(code, 2)

    def test_stat_only_and_timezone(self):
        # given this test file
        target = Path(__file__)
        # when
        res = audit.audit_file(str(target), tz=timezone.utc, platform_name="nt")
        # then
        self.assertIsNotNone(res)
        self.assertIn("os.stat()", res["limitations"])
        self.assertIn("$MFT", res["limitations"])
        self.assertIn("+0000", res["created_time"])
        self.assertIn("Windows creation time", res["ctime_semantics"])
        self.assertEqual(len(res["sha256"]), 64)
        self.assertIn("md5_legacy", res)
        self.assertNotIn("is_inverted", res)

    def test_copy_like_ctime_not_called_tamper(self):
        # given created > modified
        later = datetime(2024, 1, 16, 15, 0, tzinfo=timezone.utc).timestamp()
        earlier = datetime(2024, 1, 16, 14, 0, tzinfo=timezone.utc).timestamp()

        class FakeStat:
            st_ctime = later
            st_mtime = earlier
            st_atime = later
            st_size = 1

        original_exists = audit.os.path.exists
        original_stat = audit.os.stat
        original_hashes = audit.compute_hashes
        try:
            audit.os.path.exists = lambda _p: True
            audit.os.stat = lambda _p: FakeStat()
            audit.compute_hashes = lambda _p: ("d" * 32, "a" * 64)
            res = audit.audit_file("fake.bin", tz=timezone.utc, platform_name="nt")
        finally:
            audit.os.path.exists = original_exists
            audit.os.stat = original_stat
            audit.compute_hashes = original_hashes

        # then
        self.assertTrue(res["created_gt_modified"])
        self.assertIn("복사/다운로드", res["analysis_note"])
        self.assertNotIn("역전 발견", res["analysis_note"])
        self.assertNotIn("조작 가능성", res["analysis_note"])

    def test_posix_ctime_is_not_reported_as_creation(self):
        class FakeStat:
            st_ctime = 2
            st_mtime = 1
            st_atime = 2
            st_size = 1

        original_exists = audit.os.path.exists
        original_stat = audit.os.stat
        original_hashes = audit.compute_hashes
        try:
            audit.os.path.exists = lambda _p: True
            audit.os.stat = lambda _p: FakeStat()
            audit.compute_hashes = lambda _p: ("d" * 32, "a" * 64)
            res = audit.audit_file("fake.bin", tz=timezone.utc, platform_name="posix")
        finally:
            audit.os.path.exists = original_exists
            audit.os.stat = original_stat
            audit.compute_hashes = original_hashes

        self.assertEqual(res["created_time"], "N/A")
        self.assertFalse(res["created_gt_modified"])
        self.assertIn("not file creation", res["ctime_semantics"])


class KakaoTests(unittest.TestCase):
    def test_mobile_format(self):
        # given mobile export
        msgs = kakao.parse_kakao_file(str(FIXTURES / "kakao_mobile.txt"))
        # then
        self.assertEqual(len(msgs), 3)
        self.assertEqual(msgs[0]["timestamp"], "2024-01-16 14:15:00")
        self.assertEqual(msgs[1]["timestamp"], "2024-01-16 00:05:00")
        self.assertEqual(msgs[2]["timestamp"], "2024-01-16 12:00:00")
        self.assertTrue(msgs[1]["has_attachment"])
        self.assertIn("두 번째 줄", msgs[2]["message"])
        self.assertEqual(msgs[0]["second_precision"], "export-has-no-seconds")

    def test_pc_format(self):
        # given PC export
        msgs = kakao.parse_kakao_file(str(FIXTURES / "kakao_pc.txt"))
        # then
        self.assertEqual(len(msgs), 2)
        self.assertEqual(msgs[0]["timestamp"], "2024-01-16 14:15:22")
        self.assertTrue(msgs[1]["has_attachment"])

    def test_utf16(self):
        # given UTF-16 LE export
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "kakao16.txt"
            text = "--------------- 2024년 1월 16일 화요일 ---------------\n[홍길동] [오후 2:15] 안녕\n"
            path.write_bytes(text.encode("utf-16"))
            # when
            msgs = kakao.parse_kakao_file(str(path))
            # then
            self.assertEqual(len(msgs), 1)
            self.assertEqual(msgs[0]["sender"], "홍길동")

    def test_mobile_without_date_header_has_unknown_timestamp(self):
        msgs = kakao.parse_kakao_text("[홍길동] [오후 2:15] 날짜 없음")
        self.assertEqual(len(msgs), 1)
        self.assertIsNone(msgs[0]["timestamp"])
        self.assertTrue(msgs[0]["timestamp_unknown"])

    def test_pc_sender_may_contain_colon(self):
        msgs = kakao.parse_kakao_text("[2024-01-16 14:15:22] 팀:홍길동: 안녕하세요.")
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0]["sender"], "팀:홍길동")


class ForensicVideoTests(unittest.TestCase):
    def test_external_transcription_is_opt_in(self):
        # given an API key appears to be configured
        original_load_key = video_whisper.load_api_key
        original_extract = video_whisper.extract_audio
        calls = []
        try:
            video_whisper.load_api_key = lambda _backend=None: ("secret", "groq")
            video_whisper.extract_audio = lambda *_args: calls.append("extract")
            # when upload consent is absent
            result = video_whisper.transcribe_video("evidence.mp4", Path("."), backend="groq")
        finally:
            video_whisper.load_api_key = original_load_key
            video_whisper.extract_audio = original_extract

        # then the evidence audio is not extracted or uploaded
        self.assertEqual(result, [])
        self.assertEqual(calls, [])

    def test_video_frame_profiles_are_bounded(self):
        self.assertEqual(video_config.frame_cap("efficient"), 50)
        self.assertEqual(video_config.frame_cap("balanced"), 100)
        self.assertNotIn("token-burner", video_config.DETAIL_CAPS)


class ClaimHonestyTests(unittest.TestCase):
    def test_plugin_does_not_claim_court_admissible(self):
        data = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
        blob = json.dumps(data, ensure_ascii=False).lower()
        self.assertIn("not a forensic acquisition or court-admissibility suite", blob)
        caps = " ".join(data["interface"]["capabilities"]).lower()
        self.assertNotIn("court-admissible", caps)

    def test_core_skills_drop_overclaim_examples(self):
        kakao_skill = (ROOT / "skills/kakao-chat-extractor/SKILL.md").read_text(encoding="utf-8")
        audit_skill = (ROOT / "skills/forensic-audit/SKILL.md").read_text(encoding="utf-8")
        report = (ROOT / "templates/forensic_report_template.md").read_text(encoding="utf-8")
        contract = (ROOT / "templates/contract_template.md").read_text(encoding="utf-8")
        self.assertNotIn("정시원", kakao_skill)
        self.assertNotIn("최백랑", kakao_skill)
        self.assertIn("하지 않는 일", kakao_skill)
        self.assertIn("SQLite", kakao_skill)
        self.assertIn("하지 않는 일", audit_skill)
        self.assertIn("$MFT", audit_skill)
        self.assertNotIn("명백히 입증", report)
        self.assertNotIn("주민번호 / 사업자번호", contract)


if __name__ == "__main__":
    unittest.main()
