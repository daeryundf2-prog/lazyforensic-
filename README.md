# LazyForensic

Google Antigravity + **Gemini 3.7 Flash (High)** 용 DFIR **초안 보조** 플러그인.

법원 제출 적격 감정 스위트가 아니다. `$MFT` 파서, Timestomping 판정기, 법률 자문 엔진이 아니다.

세션이 뜨면 `hooks.json`이 `GEMINI.md`를 주입한다. 서브에이전트는 `invoke_subagent`의 `Subagents[].Model` (`flash` / `pro` / `flash_lite`)만 쓴다. `view_file`, `model_tier`, OpenCode `task`는 호스트 API가 아니다.

벤더 카탈로그(`mengto-skills/`, `design-systems/`, `vendor/antv-infographic/`)는 스킬 피커에 올리지 않는다. `INDEX.md`에서 하나만 고른 뒤 Read 한다.

---

## 실제 구현 범위

| 구성 | 하는 일 | 하지 않는 일 |
| :--- | :--- | :--- |
| `forensic-timeline` | `--input` JSON → HTML | 입력 없이 샘플 유출 사건 생성, `$MFT` 수집 |
| `forensic-audit` | `os.stat` + SHA-256/MD5 | `$SI` vs `$FN`, Maya, MOV `mvhd` |
| `kakao-chat-extractor` | 모바일/PC **텍스트 내보내기** | SQLite `chat_logs`, 백업 DB |
| `forensic-report` | 중립 보고서 초안 | "명백히 입증", 법원 유효 단정 |
| `legal-forensic-consult` | 계약 서식 빈칸, 법령 조회 보조 | 법률 자문 |
| `dlp-leakage-detector` | 사람이 로그를 맞추는 체크리스트 | 자동 탐지 스크립트 |
| `forensic-video` | ffmpeg/ffprobe 있으면 프레임·태그 추출 | 촬영일시 조작의 법정 증명 |
| `video-editor` | 클립/필름스트립 보조 | 원본을 대체하는 무손실 감정본 |
| `korean-law-mcp` | 법제처 API 클라이언트 **소스** | 빌드 없이 즉시 기동, 변호사 대체 |
| `korean-writing-reviewer` | 한국어 문장 검토 | 사실 생성 |
| `design-systems`, `mengto-skills`, `slopslap` | 벤더 UI 카탈로그 | 포렌식 엔진 |

---

## 빠른 시작

타임라인은 입력 JSON이 필수다.

```bash
python skills/forensic-timeline/scripts/generate_timeline.py --input events.json --output timeline.html
python skills/forensic-audit/scripts/audit_timestamps.py "대상파일.ext"
python skills/kakao-chat-extractor/scripts/parse_kakao.py "카카오톡_대화내용.txt" --output parsed.json
python -m unittest discover -s test -v
```

`events.json` 예:

```json
[
  {
    "timestamp": "2024-01-16 14:02:11",
    "category": "system",
    "description": "로그온",
    "details": "EventID 4624"
  }
]
```

---

## Korean Law MCP

`mcp_config.json`은 실패 폐쇄 래퍼 `scripts/korean_law_mcp.mjs`를 실행한다.
래퍼는 `korean-law-mcp/build/index.js`와 `LAW_OC`/`KOREAN_LAW_API_KEY`를 모두 확인한다.
둘 중 하나라도 없으면 명확한 오류로 종료하며 MCP 서버를 시작하지 않는다.

```bash
cd korean-law-mcp
npm install --ignore-scripts
npm run build
```

법제처 키는 `LAW_OC` 또는 `KOREAN_LAW_API_KEY`로 넣는다. 공개 폴백 서버는 쿼터/429가 있다.  
조회 결과는 법률 자문이 아니다.

인포그래픽 렌더러도 실패 폐쇄한다. 입력 `.infographic` 파일과 검토한 로컬 AntV 번들(또는 명시한 고정 HTTPS URL)이 모두 필요하며, 샘플 감정 절차와 `@latest` CDN을 자동 생성하지 않는다.

---

## Third-party trees

루트 라이선스는 MIT다. 아래 트리는 각자 고지/저작권을 따른다.

| 경로 | 출처 | 비고 |
| :--- | :--- | :--- |
| `korean-law-mcp/` | chrisryugj/korean-law-mcp (MIT, Copyright Chris) | 원 고지 유지 |
| `skills/slopslap/` | vibedesignlab/slopslap | 원 라이선스 확인 필요 |
| `design-systems/` | VoltAgent 브랜드 DESIGN.md 카탈로그 | 브랜드 상표/디자인 자산. 상업 재배포 전 검토 |
| `mengto-skills/` | Meng To / DesignCode 스킬·데모 | 저작권·이미지 재배포 위험 |

이 트리들을 포렌식 증거 도구로 광고하지 않는다. 삭제 여부는 별도 결정.

---

## 라이선스

MIT License. `LICENSE` 참고.
