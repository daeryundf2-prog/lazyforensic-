#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render_infographic.py
Renders AntV Infographic DSL into a standalone interactive HTML/SVG visualization.
Supports legal/forensic themes, responsive containers, and SVG export.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<script src="https://cdn.jsdelivr.net/npm/@antv/infographic@latest/dist/infographic.min.js"></script>
<style>
  :root {{
    --bg-main: #f8fafc;
    --bg-card: #ffffff;
    --border: #e2e8f0;
    --primary: #1e3a8a;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Pretendard", "Segoe UI", Roboto, "Malgun Gothic", sans-serif;
    background-color: var(--bg-main);
    color: #0f172a;
    padding: 24px;
    display: flex;
    flex-direction: column;
    align-items: center;
  }}
  .header {{
    max-width: 1200px;
    width: 100%;
    margin-bottom: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #ffffff;
    padding: 16px 24px;
    border-radius: 8px;
    border: 1px solid var(--border);
  }}
  .header h1 {{ font-size: 20px; font-weight: 700; color: var(--primary); }}
  .badge {{ font-size: 12px; background: #e0e7ff; color: #3730a3; padding: 4px 10px; border-radius: 9999px; font-weight: 600; }}
  #container {{
    max-width: 1200px;
    width: 100%;
    min-height: 650px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    display: flex;
    justify-content: center;
    align-items: center;
  }}
  .controls {{
    margin-top: 16px;
    display: flex;
    gap: 8px;
  }}
  .btn {{
    padding: 8px 16px;
    background: var(--primary);
    color: #ffffff;
    border: none;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
  }}
  .btn:hover {{ opacity: 0.9; }}
</style>
</head>
<body>
<div class="header">
  <h1>{title}</h1>
  <span class="badge">AntV Infographic Visualizer</span>
</div>

<div id="container"></div>

<div class="controls">
  <button class="btn" onclick="window.print()">🖨️ 인쇄 / PDF 저장</button>
</div>

<script>
const dslContent = `{dsl_escaped}`;

try {{
  const infographic = new AntVInfographic.Infographic({{
    container: '#container',
    width: '100%',
    height: '100%',
    editable: true,
  }});
  infographic.render(dslContent);
}} catch (err) {{
  console.error("Render failed:", err);
  document.getElementById('container').innerHTML = '<div style="color:red;padding:20px;">인포그래픽 렌더링 오류: ' + err.message + '</div>';
}}
</script>
</body>
</html>
"""


def render_infographic_html(dsl_text: str, output_path: str, title: str = "디지털포렌식 시각화 인포그래픽") -> str:
    dsl_escaped = dsl_text.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
    html = HTML_TEMPLATE.format(
        title=title,
        dsl_escaped=dsl_escaped
    )
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_path


def main():
    parser = argparse.ArgumentParser(description="AntV Infographic Standalone HTML Renderer")
    parser.add_argument("input", nargs="?", help="Input .infographic file or text")
    parser.add_argument("--output", default="infographic_preview.html", help="Output HTML file path")
    parser.add_argument("--title", default="포렌식 분석 인포그래픽", help="Infographic title")
    args = parser.parse_args()

    if args.input and Path(args.input).exists():
        with open(args.input, "r", encoding="utf-8") as f:
            dsl = f.read()
    elif args.input:
        dsl = args.input
    else:
        # Sample forensic process infographic
        dsl = """infographic list-row-horizontal-icon-arrow
data
  title 디지털포렌식 정규 감정 절차
  desc 법무법인(유한) 대륜 디지털포렌식센터
  lists
    - label 1. 증거 획득
      desc 쓰기방지 장치 연결 및 E01/L01 포렌식 이미징
      icon shield
    - label 2. 무결성 검증
      desc 원본/사본 SHA-256 해시 대조 및 CoC 확보
      icon check-circle
    - label 3. 정밀 분석
      desc 타임스탬프, 타임라인, 아티팩트 복구
      icon search
    - label 4. 감정서 발행
      desc 법원 제출용 정식 포렌식 감정의견서 작성
      icon file-text
theme
  palette #1e3a8a #3b82f6 #10b981 #6366f1
"""

    out_file = render_infographic_html(dsl, args.output, title=args.title)
    print(f"[+] Infographic HTML successfully generated: {out_file}")


if __name__ == "__main__":
    main()
