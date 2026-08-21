import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
MAX_DESCRIPTION = 280
VISIBLE_SKILL_CAP = 16


def skill_md_files():
    return sorted(SKILLS.rglob("SKILL.md"))


def frontmatter_description(text):
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    if end < 0:
        return ""
    block = text[3:end]
    match = re.search(r"^description:\s*(.+)$", block, re.MULTILINE)
    if match is None:
        return ""
    return match.group(1).strip().strip("\"'")


class GeminiCatalogTests(unittest.TestCase):
    def test_visible_skill_count_is_bounded(self):
        # given skills/ is the Antigravity picker root
        files = skill_md_files()
        # then vendor satellites are not registered
        self.assertEqual(len(files), VISIBLE_SKILL_CAP)
        names = {path.parent.name for path in files}
        self.assertIn("lazyforensic", names)
        self.assertIn("ui-studio", names)
        self.assertNotIn("infographic-syntax-creator", names)
        self.assertNotIn("manim-video", names)
        self.assertNotIn("slopslap", names)
        self.assertNotIn("frontend-ui-ux", names)
        self.assertNotIn("design-system", names)

    def test_descriptions_fit_flash_picker(self):
        # given every visible SKILL.md
        for path in skill_md_files():
            desc = frontmatter_description(path.read_text(encoding="utf-8"))
            # then description is short enough to stay in Gemini skill catalog
            self.assertTrue(desc, path)
            self.assertLessEqual(len(desc), MAX_DESCRIPTION, f"{path}: {len(desc)} {desc}")

    def test_visible_skill_descriptions_omit_foreign_apis(self):
        # given picker descriptions (always in Gemini context)
        for path in skill_md_files():
            desc = frontmatter_description(path.read_text(encoding="utf-8"))
            # then do not advertise foreign tools as capabilities
            self.assertNotIn("model_tier", desc, path)
            self.assertNotIn("CLAUDE_PLUGIN_ROOT", desc, path)
            self.assertNotIn("subagent_type", desc, path)

    def test_plugin_wires_hooks_and_gemini_default(self):
        data = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(data["hooks"], "./hooks.json")
        self.assertIn("Gemini 3.7 Flash", data["description"])
        hooks = json.loads((ROOT / "hooks.json").read_text(encoding="utf-8"))
        command = hooks["hooks"]["SessionStart"][0]["hooks"][0]["command"]
        self.assertIn("session_start.mjs", command)

    def test_session_start_injects_gemini_md(self):
        # given SessionStart stdin
        payload = json.dumps({"hook_event_name": "SessionStart"})
        # when
        proc = subprocess.run(
            ["node", str(ROOT / "scripts" / "session_start.mjs")],
            input=payload,
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
            cwd=str(ROOT),
        )
        # then
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = json.loads(proc.stdout)
        ctx = out["hookSpecificOutput"]["additionalContext"]
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "SessionStart")
        self.assertIn("invoke_subagent", ctx)
        self.assertIn("실패 폐쇄", ctx)
        self.assertIn("호스트 `Read`", ctx)
        self.assertIn("증거 오디오", ctx)
        self.assertRegex(ctx, r"korean_law: (ready|missing-build|missing-LAW_OC)")
        self.assertNotIn("LAW_OC=", ctx)

    def test_vendor_antv_kept_off_catalog(self):
        vendor = ROOT / "vendor" / "antv-infographic" / "creator-full.md"
        self.assertTrue(vendor.is_file())
        self.assertFalse((SKILLS / "infographic-syntax-creator" / "SKILL.md").exists())
        self.assertTrue((SKILLS / "video-editor" / "manim-video" / "REFERENCE.md").is_file())
        self.assertFalse((SKILLS / "video-editor" / "manim-video" / "SKILL.md").exists())
        self.assertTrue((SKILLS / "slopslap" / "REFERENCE.md").is_file())
        self.assertFalse((SKILLS / "slopslap" / "SKILL.md").exists())
        self.assertFalse((SKILLS / "frontend-ui-ux" / "SKILL.md").exists())
        self.assertFalse((SKILLS / "design-system" / "SKILL.md").exists())

    def test_infographic_cli_fails_closed_without_input(self):
        # given no input artifact
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "infographic.html"
            # when
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SKILLS / "infographic-creator" / "scripts" / "render_infographic.py"),
                    "--output",
                    str(output),
                ],
                text=True,
                encoding="utf-8",
                capture_output=True,
                check=False,
                cwd=str(ROOT),
            )
            # then
            self.assertEqual(proc.returncode, 2)
            self.assertFalse(output.exists())
            source = (SKILLS / "infographic-creator" / "scripts" / "render_infographic.py").read_text(
                encoding="utf-8"
            )
            self.assertNotIn("법무법인(유한) 대륜", source)
            self.assertNotIn("@latest", source)

    def test_law_mcp_wrapper_refuses_missing_key(self):
        # given a clean environment without a law API key
        env = os.environ.copy()
        env.pop("LAW_OC", None)
        env.pop("KOREAN_LAW_API_KEY", None)
        # when
        proc = subprocess.run(
            ["node", str(ROOT / "scripts" / "korean_law_mcp.mjs")],
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
            cwd=str(ROOT),
            env=env,
        )
        # then
        self.assertEqual(proc.returncode, 78)
        self.assertIn("disabled", proc.stderr)
        self.assertIn("LAW_OC", proc.stderr)

    def test_distribution_marks_unverified_vendor_rights(self):
        notice = (ROOT / "NOTICE").read_text(encoding="utf-8")
        self.assertIn("korean-law-mcp/LICENSE", notice)
        self.assertIn("No license file is present", notice)
        self.assertIn("trademark", notice)

        ignored = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("timeline_report.html", ignored)
        self.assertIn("infographic_preview.html", ignored)
        self.assertIn("korean-law-mcp/build/", ignored)
        self.assertIn(".env", ignored)

    def test_catalog_indexes_list_full_trees(self):
        mengto = (ROOT / "mengto-skills" / "INDEX.md").read_text(encoding="utf-8")
        brands = (ROOT / "design-systems" / "INDEX.md").read_text(encoding="utf-8")
        antv = (ROOT / "vendor" / "antv-infographic" / "INDEX.md").read_text(encoding="utf-8")
        self.assertIn("Do not glob", mengto)
        self.assertIn("Do not glob", brands)
        self.assertIn("Do not glob", antv)
        self.assertGreaterEqual(mengto.count("`"), 127)
        self.assertGreaterEqual(brands.count("| `"), 74)
        self.assertIn("creator-full.md", antv)
        self.assertIn("infographic-syntax-creator/SKILL.md", antv)

    def test_session_start_does_not_leak_law_key(self):
        env = os.environ.copy()
        env["LAW_OC"] = "secret-law-key-should-not-appear"
        payload = json.dumps({"hook_event_name": "SessionStart"})
        proc = subprocess.run(
            ["node", str(ROOT / "scripts" / "session_start.mjs")],
            input=payload,
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
            cwd=str(ROOT),
            env=env,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertNotIn("secret-law-key-should-not-appear", proc.stdout)
        self.assertNotIn("secret-law-key-should-not-appear", proc.stderr)
        ctx = json.loads(proc.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertRegex(ctx, r"korean_law: (ready|missing-build|missing-LAW_OC)")

    def test_setup_korean_law_is_local_only(self):
        source = (ROOT / "scripts" / "setup_korean_law.mjs").read_text(encoding="utf-8")
        self.assertIn("npm", source)
        self.assertIn("--ignore-scripts", source)
        self.assertIn("Do not fly deploy", source)
        self.assertNotIn("fly deploy", source.replace("Do not fly deploy", ""))
        self.assertTrue((ROOT / ".env.example").is_file())
        example = (ROOT / ".env.example").read_text(encoding="utf-8")
        self.assertIn("LAW_OC=", example)
        self.assertNotRegex(example, r"LAW_OC=\S+")

    def test_plugin_version_and_lane_copy(self):
        data = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(data["version"], "1.0.0")
        self.assertIn("lanes", data["interface"]["longDescription"].lower())
        self.assertIn("not a forensic acquisition or court-admissibility suite", json.dumps(data, ensure_ascii=False).lower())
        self.assertTrue((ROOT / "docs" / "GAPS.md").is_file())
        self.assertTrue((SKILLS / "ui-studio" / "SKILL.md").is_file())

    def test_help_guide_is_routed_without_expanding_picker(self):
        guide = (ROOT / "docs" / "USER_GUIDE.md").read_text(encoding="utf-8")
        router = (SKILLS / "lazyforensic" / "SKILL.md").read_text(encoding="utf-8")
        gemini = (ROOT / "GEMINI.md").read_text(encoding="utf-8")
        self.assertIn("설명서", guide)
        self.assertIn("보고서 완성 워크플로", guide)
        self.assertIn("디자인 검토", guide)
        self.assertIn("generate_timeline.py --input", guide)
        self.assertIn("docs/USER_GUIDE.md", router)
        self.assertIn("docs/USER_GUIDE.md", gemini)
        self.assertEqual(len(skill_md_files()), VISIBLE_SKILL_CAP)


if __name__ == "__main__":
    unittest.main()
