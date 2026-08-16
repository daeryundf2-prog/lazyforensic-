# LazyForensic

Google Antigravity + **Gemini 3.7 Flash (High)** 용 DFIR **초안 보조** 플러그인.

법원 제출 적격 감정 스위트가 아니다. `$MFT` 파서, Timestomping 판정기, 법률 자문 엔진이 아니다.

세션이 뜨면 `hooks.json`이 한국어 `GEMINI.md`를 주입한다. 서브에이전트는 `invoke_subagent`의 `Subagents[].Model` (`flash` / `pro` / `flash_lite`)만 쓴다. `view_file`, `model_tier`, OpenCode `task`는 호스트 API가 아니다.

기본 스킬 피커는 12개(`SKILL.md`)만 둔다. 벤더 카탈로그는 레인 → INDEX → 파일 하나로 도달한다. `mengto-skills/**`, `design-systems/**`, `vendor/**`를 glob 하지 않는다.
Node가 없거나 SessionStart 훅이 실패하면 `GEMINI.md`를 직접 읽은 뒤 진행한다.

구현하지 않은 능력은 `docs/GAPS.md`에 있다.
채팅에 `설명서`, `도움말`, `명령어 알려줘`라고 입력하면 `docs/USER_GUIDE.md`의 기능별 요청 예시를 안내한다.

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

## 레인 사용

한 턴에 레인 하나만 고른다.

- 포렌식 기본(타임라인·해시·카카오 txt·감정서): `skills/lazyforensic/SKILL.md`
- 인포그래픽: `skills/infographic-creator/SKILL.md` → 필요 시 `vendor/antv-infographic/INDEX.md`에서 하나
- 뷰어/슬롭/브랜드 토큰: `skills/ui-studio/SKILL.md` → REFERENCE 하나 → INDEX에서 하나
- 법령 조문: `node scripts/setup_korean_law.mjs` 후 `LAW_OC` 설정, 그다음 `korean_law` MCP. 키가 없으면 조문을 만들지 않는다.

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

## 실행 환경

| 기능 | 필수 | 선택 |
| :--- | :--- | :--- |
| 타임라인·해시·카카오 txt | Python 3.10+ 표준 라이브러리 | 없음 |
| 영상 프레임·메타데이터 | Python 3.10+, `ffmpeg`, `ffprobe` | URL 다운로드용 `yt-dlp` |
| 영상 필름스트립 | 위 항목 + `numpy`, `Pillow` | 외부 전사용 `requests` |
| Korean Law MCP | Node.js 20.19+, `npm install --ignore-scripts`, `npm run build` | 없음 |
| SessionStart 계약 주입 | Node.js 20+ | 실패 시 `GEMINI.md` 직접 Read |

외부 전사는 기본 비활성화다. `--upload-audio`를 명시하면 추출 오디오가 Groq 또는 OpenAI로 전송되므로 의뢰인 동의와 반출 승인을 먼저 확인한다.

---

## Korean Law MCP

`mcp_config.json`은 실패 폐쇄 래퍼 `scripts/korean_law_mcp.mjs`를 실행한다.
래퍼는 `korean-law-mcp/build/index.js`와 `LAW_OC`/`KOREAN_LAW_API_KEY`를 모두 확인한다.
둘 중 하나라도 없으면 명확한 오류로 종료하며 MCP 서버를 시작하지 않는다.

```bash
node scripts/setup_korean_law.mjs
```

또는 수동으로:

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

루트 라이선스는 원본 LazyForensic 파일에 적용된다. 벤더 트리는 각자 고지/저작권을 따르며 상세 위험은 `NOTICE`에 기록한다.

| 경로 | 출처 | 비고 |
| :--- | :--- | :--- |
| `korean-law-mcp/` | chrisryugj/korean-law-mcp (MIT, Copyright Chris) | 원 고지 유지 |
| `skills/slopslap/` | vibedesignlab/slopslap | 라이선스 파일 없음. 별도 권리 확인 필요 |
| `design-systems/` | VoltAgent 브랜드 DESIGN.md 카탈로그 | 상표·브랜드 디자인 권리 별도 검토 |
| `mengto-skills/` | Meng To / DesignCode 스킬·데모 | 라이선스 파일 없음. 별도 권리 확인 필요 |
| `vendor/antv-infographic/` | AntV Infographic 생태계 참고 자료 | JS 번들 권리는 별도 검토 |

이 트리들을 포렌식 증거 도구로 광고하지 않는다. 삭제 여부는 별도 결정.

---

## 라이선스

MIT License. `LICENSE` 참고.
