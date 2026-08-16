import json
import re
import subprocess
import sys
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
        self.assertLessEqual(len(files), VISIBLE_SKILL_CAP)
        names = {path.parent.name for path in files}
        self.assertIn("lazyforensic", names)
        self.assertNotIn("infographic-syntax-creator", names)
        self.assertNotIn("manim-video", names)

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
        self.assertIn("Fail closed", ctx)
        self.assertIn("host `Read`", ctx)

    def test_vendor_antv_kept_off_catalog(self):
        vendor = ROOT / "vendor" / "antv-infographic" / "creator-full.md"
        self.assertTrue(vendor.is_file())
        self.assertFalse((SKILLS / "infographic-syntax-creator" / "SKILL.md").exists())
        self.assertTrue((SKILLS / "video-editor" / "manim-video" / "REFERENCE.md").is_file())
        self.assertFalse((SKILLS / "video-editor" / "manim-video" / "SKILL.md").exists())


if __name__ == "__main__":
    unittest.main()
