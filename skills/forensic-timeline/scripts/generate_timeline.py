#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_timeline.py
Digital Forensic Interactive Timeline Generator
Generates standalone HTML timeline with search, category filtering, and print-optimized CSS.
"""

import sys
import json
import argparse
from datetime import datetime

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  :root {{
    --bg-main: #f8fafc;
    --bg-card: #ffffff;
    --text-primary: #0f172a;
    --text-secondary: #475569;
    --border-color: #e2e8f0;
    --primary: #1e3a8a;
    --primary-light: #3b82f6;
    --danger: #dc2626;
    --warning: #d97706;
    --success: #16a34a;
    --accent: #6366f1;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Pretendard", "Segoe UI", Roboto, "Malgun Gothic", sans-serif;
    background-color: var(--bg-main);
    color: var(--text-primary);
    line-height: 1.6;
    padding: 24px;
  }}
  .container {{
    max-width: 1200px;
    margin: 0 auto;
  }}
  header {{
    background: linear-gradient(135deg, #1e3a8a 0%, #1e293b 100%);
    color: #ffffff;
    padding: 32px;
    border-radius: 12px;
    margin-bottom: 24px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  }}
  header h1 {{ font-size: 24px; font-weight: 700; margin-bottom: 8px; }}
  header p {{ font-size: 14px; opacity: 0.9; }}
  .meta-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin-top: 20px;
    padding-top: 16px;
    border-top: 1px solid rgba(255, 255, 255, 0.2);
  }}
  .meta-item {{ font-size: 13px; }}
  .meta-label {{ opacity: 0.7; margin-bottom: 2px; }}
  .meta-val {{ font-weight: 600; }}
  
  .controls {{
    background: var(--bg-card);
    padding: 16px 20px;
    border-radius: 8px;
    border: 1px solid var(--border-color);
    margin-bottom: 24px;
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    align-items: center;
    justify-content: space-between;
  }}
  .search-box input {{
    padding: 8px 14px;
    border: 1px solid var(--border-color);
    border-radius: 6px;
    font-size: 14px;
    width: 280px;
    outline: none;
  }}
  .search-box input:focus {{
    border-color: var(--primary-light);
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
  }}
  .filter-btns {{
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
  }}
  .btn {{
    padding: 6px 12px;
    border-radius: 6px;
    border: 1px solid var(--border-color);
    background: #ffffff;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s ease;
  }}
  .btn.active, .btn:hover {{
    background: var(--primary);
    color: #ffffff;
    border-color: var(--primary);
  }}
  
  /* Timeline Layout */
  .timeline {{
    position: relative;
    padding-left: 32px;
  }}
  .timeline::before {{
    content: '';
    position: absolute;
    left: 11px;
    top: 8px;
    bottom: 8px;
    width: 2px;
    background: #cbd5e1;
  }}
  .timeline-item {{
    position: relative;
    margin-bottom: 20px;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 16px 20px;
    transition: transform 0.1s ease, box-shadow 0.1s ease;
  }}
  .timeline-item:hover {{
    transform: translateX(4px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  }}
  .timeline-item::before {{
    content: '';
    position: absolute;
    left: -27px;
    top: 20px;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: #64748b;
    border: 2px solid #ffffff;
    box-shadow: 0 0 0 2px #cbd5e1;
  }}
  .timeline-item.tag-critical::before {{ background: var(--danger); box-shadow: 0 0 0 2px #fecaca; }}
  .timeline-item.tag-file::before {{ background: var(--primary-light); box-shadow: 0 0 0 2px #bfdbfe; }}
  .timeline-item.tag-web::before {{ background: var(--warning); box-shadow: 0 0 0 2px #fef3c7; }}
  .timeline-item.tag-chat::before {{ background: var(--accent); box-shadow: 0 0 0 2px #e0e7ff; }}
  .timeline-item.tag-system::before {{ background: var(--success); box-shadow: 0 0 0 2px #bbf7d0; }}

  .item-header {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 8px;
    flex-wrap: wrap;
    gap: 8px;
  }}
  .item-time {{
    font-size: 15px;
    font-weight: 700;
    color: var(--primary);
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  }}
  .item-badge {{
    display: inline-block;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
  }}
  .badge-critical {{ background: #fee2e2; color: #991b1b; }}
  .badge-file {{ background: #dbeafe; color: #1e40af; }}
  .badge-web {{ background: #fef3c7; color: #92400e; }}
  .badge-chat {{ background: #ede9fe; color: #5b21b6; }}
  .badge-system {{ background: #dcfce7; color: #166534; }}

  .item-body {{
    font-size: 14px;
    color: var(--text-primary);
  }}
  .item-desc {{
    font-weight: 600;
    margin-bottom: 4px;
  }}
  .item-details {{
    font-size: 13px;
    color: var(--text-secondary);
    background: #f1f5f9;
    padding: 8px 12px;
    border-radius: 4px;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    word-break: break-all;
    margin-top: 6px;
  }}

  @media print {{
    body {{ background: #ffffff; padding: 0; }}
    .controls {{ display: none; }}
    header {{ background: #1e293b; color: #ffffff; padding: 20px; }}
    .timeline-item {{ break-inside: avoid; border: 1px solid #cbd5e1; }}
  }}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>{title}</h1>
    <p>법무법인(유한) 대륜 디지털포렌식센터 시계열 전수 타임라인 분석 보고서</p>
    <div class="meta-grid">
      <div class="meta-item"><div class="meta-label">분석 대상</div><div class="meta-val">{target}</div></div>
      <div class="meta-item"><div class="meta-label">분석 일자</div><div class="meta-val">{analyzed_at}</div></div>
      <div class="meta-item"><div class="meta-label">총 이벤트 건수</div><div class="meta-val">{total_events} 건</div></div>
      <div class="meta-item"><div class="meta-label">타임존</div><div class="meta-val">KST (UTC+09:00)</div></div>
    </div>
  </header>

  <div class="controls">
    <div class="search-box">
      <input type="text" id="searchInput" placeholder="키워드/파일명/행위 검색..." onkeyup="filterTimeline()">
    </div>
    <div class="filter-btns">
      <button class="btn active" onclick="setCategory('all', this)">전체</button>
      <button class="btn" onclick="setCategory('critical', this)">🚨 유출/의심</button>
      <button class="btn" onclick="setCategory('file', this)">📁 파일 행위</button>
      <button class="btn" onclick="setCategory('web', this)">🌐 웹/검색</button>
      <button class="btn" onclick="setCategory('chat', this)">💬 메신저/대화</button>
      <button class="btn" onclick="setCategory('system', this)">⚙️ 시스템</button>
    </div>
  </div>

  <div class="timeline" id="timelineList">
    {timeline_items}
  </div>
</div>

<script>
let currentCategory = 'all';

function setCategory(cat, btn) {{
  currentCategory = cat;
  document.querySelectorAll('.filter-btns .btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  filterTimeline();
}}

function filterTimeline() {{
  const query = document.getElementById('searchInput').value.toLowerCase();
  const items = document.querySelectorAll('.timeline-item');
  
  items.forEach(item => {{
    const cat = item.getAttribute('data-category');
    const text = item.innerText.toLowerCase();
    
    const matchesCat = (currentCategory === 'all' || cat === currentCategory);
    const matchesQuery = text.includes(query);
    
    if (matchesCat && matchesQuery) {{
      item.style.display = 'block';
    }} else {{
      item.style.display = 'none';
    }}
  }});
}}
</script>
</body>
</html>
"""

def generate_html(events, title="디지털포렌식 시계열 타임라인", target="피분석 기기 / 저장매체"):
    items_html = []
    category_map = {
        'critical': ('tag-critical', 'badge-critical', '🚨 유출의심'),
        'file': ('tag-file', 'badge-file', '📁 파일행위'),
        'web': ('tag-web', 'badge-web', '🌐 웹/검색'),
        'chat': ('tag-chat', 'badge-chat', '💬 메신저'),
        'system': ('tag-system', 'badge-system', '⚙️ 시스템'),
    }

    for ev in events:
        cat = ev.get('category', 'file').lower()
        if cat not in category_map:
            cat = 'file'
        tag_cls, badge_cls, badge_label = category_map[cat]
        time_str = ev.get('timestamp', '-')
        desc = ev.get('description', '')
        details = ev.get('details', '')
        
        detail_html = f'<div class="item-details">{details}</div>' if details else ''

        item = f"""
        <div class="timeline-item {tag_cls}" data-category="{cat}">
          <div class="item-header">
            <span class="item-time">{time_str}</span>
            <span class="item-badge {badge_cls}">{badge_label}</span>
          </div>
          <div class="item-body">
            <div class="item-desc">{desc}</div>
            {detail_html}
          </div>
        </div>
        """
        items_html.append(item)

    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return HTML_TEMPLATE.format(
        title=title,
        target=target,
        analyzed_at=now_str,
        total_events=len(events),
        timeline_items="\n".join(items_html)
    )

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Forensic Timeline HTML Generator")
    parser.add_argument('--input', help="Input JSON file containing events list")
    parser.add_argument('--output', default="timeline_report.html", help="Output HTML path")
    parser.add_argument('--title', default="디지털포렌식 시계열 전수 타임라인", help="Report title")
    parser.add_argument('--target', default="피분석 저장매체 (PC/Mobile)", help="Target device")
    args = parser.parse_args()

    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            events_data = json.load(f)
    else:
        # Sample test data
        events_data = [
            {"timestamp": "2024-01-16 14:02:11", "category": "system", "description": "사용자 계정 로그인 성공", "details": "User: user1 | EventID: 4624 | LogonType: 2 (Interactive)"},
            {"timestamp": "2024-01-16 14:15:30", "category": "web", "description": "구글 검색: 대용량 클라우드 파일 전송", "details": "URL: https://www.google.com/search?q=대용량+클라우드+파일+전송"},
            {"timestamp": "2024-01-16 14:32:05", "category": "critical", "description": "외장 USB 드라이브 연결 및 대량 복사", "details": "Drive: E:\\ (SanDisk 64GB) | Target: 152개 핵심 도면 파일 복사"},
            {"timestamp": "2024-01-16 15:10:44", "category": "chat", "description": "카카오톡 대화방 파일 전송", "details": "Receiver: 협력사 담당자 | File: 최종_설계안.zip (48MB)"}
        ]

    html_out = generate_html(events_data, title=args.title, target=args.target)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(html_out)
    print(f"[+] Forensic Timeline successfully generated: {args.output} ({len(events_data)} events)")
