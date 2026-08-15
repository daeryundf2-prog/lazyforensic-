# LazyForensic

> **Digital Forensic & Incident Response (DFIR) Specialist Suite for Google Antigravity**  
> 법무법인(유한) 대륜 디지털포렌식센터 맞춤형 디지털 포렌식·법률 AI·감정보고서·문서 교정·동영상 증거물 가공·AI 슬롭 제거·프리미엄 UI/UX 엔지니어링 독립 플러그인

---

## 🌟 개요 (Overview)

`LazyForensic`은 Google Antigravity 에이전트 환경에서 동작하는 전문 디지털 포렌식 & 리걸테크 확장 플러그인입니다.  
개발·코딩용 플러그인(`LazyAntigravity`)과 완전히 분리되어 독립적으로 동작하며, **SlopSlap(UI AI-Slop 기계적 제거 파이프라인)**, **Meng To(DesignCode) 127개 프리미엄 UI/UX 스킬**, **74+ 브랜드 DESIGN.md 디자인 시스템**, **Korean Law MCP(법제처 법령/판례 실시간 조회·인용검증)**, **Korean Writing Reviewer(법원/로펌 공문서 전문 한국어 감수·교정)**, 법원/수사기관 제출용 포렌식 감정보고서 작성, 시계열 타임라인 자동 생성, 파일 타임스탬프 위변조 감정, CCTV/블랙박스/동영상 증거물 멀티모달 분석 및 정밀 구간 편집, AntV 전문 인포그래픽 시각화, 모바일/카카오톡 대화 분석, DLP 정보유출 교차 분석을 자동화합니다.

---

## 🖐️ UI 슬롭 기계적 제거 엔진 (SlopSlap by VibeDesignLab)

* **`slopslap`**: AI가 생성한 촌스러운 UI 클리셰(오버라인·eyebrow 뱃지, 플로팅 글로우 오브/blob, 그라디언트 텍스트, 이모지 남발, 무지개 팔레트, 불필요한 중첩 컨테이너)를 5단계 병렬 파이프라인(A~E 영역)으로 실측 감지하고 기계적으로 완벽 제거.

---

## ✨ 내장 UI/UX & 디자인 카탈로그

* **`mengto-skills/`**: Meng To(DesignCode)의 127개 프론트엔드/인터랙션 스킬 (부드러운 스크롤 타임라인, 다크 글래스모피즘, 테크니컬 와이어프레임 뷰, Three.js 3D 유출경로 시각화 등)
* **`design-systems/`**: Linear, Apple, Stripe, Vercel, Raycast, Supabase 등 74개 글로벌 최고급 브랜드 정밀 `DESIGN.md` 토큰

---

## ⚖️ 내장 MCP 서버 (Bundled MCP Server)

* **`korean_law`**: 법제처 42개 Open API 연동 대한민국 법령·대법원 판례·행정규칙 실시간 검색, 조문 영향 분석, 판례 인용 검증(Citation Verification) 엔진

---

## 🛠️ 핵심 스킬 구성 (Included Skills)

| 스킬명 | 설명 | 주요 실행 스크립트 / 레퍼런스 |
| :--- | :--- | :--- |
| **`slopslap`** | 5대 영역(대표슬롭·레이아웃·간격·타이포·색) UI AI-Slop 병렬 정적 점검 및 기계적 제거 | `scripts/scan-slop-signals.mjs`, `scripts/fetch-references.mjs` |
| **`frontend-ui-ux`** | Meng To 127개 UI/UX 스킬 기반 인터랙티브 타임라인 뷰어, 다크 글래스 대시보드, 3D WebGL 시각화 | `mengto-skills/*` |
| **`design-system`** | 74개 글로벌 브랜드 DESIGN.md 기반 타임라인 뷰어, 포렌식 대시보드, 웹 리포트 프리미엄 UI/UX 스타일링 | `design-systems/*/DESIGN.md` |
| **`korean-writing-reviewer`** | 공문서, 법률 의견서, 기술 감정서, 보고서의 전문 한국어 교정, 번역투/상투적 AI 문체 제거, 원문 수치·해시 보존 검수 | `references/scoring-report.md`, `references/editor-protection.md` |
| **`legal-forensic-consult`** | Korean Law MCP 연동 법제처 법령/판례 검색, 포렌식 위임 계약서, 보수기준표 견적, 비동의 조사/압수수색 적법성 자문 | `templates/contract_template.md` |
| **`video-editor`** | CCTV/블랙박스 증거 영상 정밀 컷팅(Trim), 오디오 파형+필름스트립 타임라인 생성, 화질 보정, 자막 번인 렌더링 | `helpers/timeline_view.py`, `helpers/render.py` |
| **`forensic-video`** | CCTV, 블랙박스, 휴대폰 촬영 동영상(.mov/.mp4), 온라인 영상 URL 멀티모달 프레임 캡처, 음성 전사(STT), 메타데이터 감정 | `scripts/watch.py`, `scripts/forensic_video_audit.py` |
| **`infographic-creator`** | AntV Infographic 엔진 기반 포렌식 절차도, 유출 경로도, 타임라인 요약 인포그래픽 SVG/HTML 생성 | `scripts/render_infographic.py` |
| **`forensic-timeline`** | PC 사용기록, $MFT, 이벤트 로그를 결합한 인터랙티브 HTML 타임라인 및 인쇄용 PDF 자동 생성 | `scripts/generate_timeline.py` |
| **`forensic-audit`** | 파일 타임스탬프($SI vs $FN), 생성일시>수정일시 역전, 미디어/Maya 메타데이터 위변조 과학수사 감정 | `scripts/audit_timestamps.py` |
| **`forensic-report`** | 법무법인 대륜 디지털포렌식센터 표준 서식 기반 공식 감정서, 기술자문 의견서 작성 및 감수 | `templates/forensic_report_template.md` |
| **`kakao-chat-extractor`** | 대용량 카카오톡/모바일 대화방 텍스트 및 DB 파싱, 특정 인물·일자·키워드 대화 추출 | `scripts/parse_kakao.py` |
| **`dlp-leakage-detector`** | 기업 내부정보 유출 시 DLP 로그, 구글 검색어, USB 연결 기록을 결합한 유출 타임라인 산출 | - |

---

## 📂 디렉토리 구조 (Directory Structure)

```text
lazyforensic/
├── plugin.json                 # 플러그인 매니페스트 (Antigravity 자동 등록)
├── mcp_config.json             # Korean Law MCP 서버 설정
├── README.md                   # 프로젝트 설명서 및 실행 가이드
├── .gitignore                  # Git 관리 제외 규칙
├── mengto-skills/              # [127개 스킬] Meng To(DesignCode) UI/UX 스킬 모음
├── design-systems/             # [74개 브랜드] Linear, Apple, Stripe 등 DESIGN.md 카탈로그
├── korean-law-mcp/             # [번들 MCP] 법제처 법령/판례 검색·인용검증 런타임
├── templates/                  # 법원/의뢰인 제출 표준 서식
│   ├── forensic_report_template.md  # 포렌식 감정의견서 템플릿
│   └── contract_template.md         # 디지털포렌식 위임계약서 서식
└── skills/
    ├── slopslap/               # [스킬] UI AI-Slop 기계적 제거 파이프라인 (VibeDesignLab)
    ├── frontend-ui-ux/         # [스킬] Meng To UI/UX 인터랙티브 웹 엔지니어링
    ├── design-system/          # [스킬] 74개 브랜드 프리미엄 UI/UX 스타일링
    ├── korean-writing-reviewer/# [스킬] 공문서/감정서 전문 한국어 문장 교정·검토
    ├── legal-forensic-consult/ # [스킬] 포렌식 법률/판례/계약 자문 (MCP 연동)
    ├── video-editor/           # [스킬] CCTV/블랙박스 증거영상 편집 & 필름스트립 생성
    ├── forensic-video/         # [스킬] CCTV/블랙박스/동영상 멀티모달 분석
    ├── infographic-creator/    # [스킬] AntV 기반 인포그래픽/다이어그램 생성
    ├── forensic-timeline/      # [스킬] 타임라인 생성
    ├── forensic-audit/         # [스킬] 타임스탬프 감정
    ├── forensic-report/        # [스킬] 감정보고서 작성
    ├── kakao-chat-extractor/   # [스킬] 카카오톡/메신저 파싱
    └── dlp-leakage-detector/   # [스킬] DLP/유출 분석
```

---

## 🚀 빠른 시작 (Quick Start)

### 1. UI 화면 AI-Slop 기계적 제거
```markdown
이 타임라인 대시보드 웹페이지에서 AI 슬롭(오버라인 뱃지, 불필요한 글로우, 중첩 컨테이너)을 깨끗하게 걷어내줘.
```

### 2. 인터랙티브 포렌식 타임라인 웹 뷰어 생성
```markdown
Meng To 스타일의 부드러운 스크롤 인터랙션과 Linear 다크 글래스 UI를 적용한 포렌식 타임라인 HTML을 만들어줘.
```

### 3. 포렌식 감정보고서 문장 교정 및 감수
```markdown
이 포렌식 감정서 초안의 어색한 번역투 문장을 다듬고, 법원 제출용 격식체로 교정해줘. (수치/해시값 절대 보존)
```

### 4. 비디오 오디오 파형 + 필름스트립 타임라인 생성
```bash
python skills/video-editor/helpers/timeline_view.py "C:\경로\CCTV.mp4" 10.0 60.0 -o timeline_strip.png
```

### 5. 동영상 증거물 분석 & 프레임 추출
```bash
python skills/forensic-video/scripts/watch.py "C:\경로\CCTV_영상.mp4" --resolution 720
```

### 6. 포렌식 인포그래픽 시각화 생성
```bash
python skills/infographic-creator/scripts/render_infographic.py --output forensic_chart.html
```

### 7. 시계열 타임라인 생성
```bash
python skills/forensic-timeline/scripts/generate_timeline.py --title "2024-01-16 PC 사용기록 전수 타임라인" --output timeline.html
```

### 8. 파일 타임스탬프 & 무결성 감정
```bash
python skills/forensic-audit/scripts/audit_timestamps.py "C:\경로\피분석파일.ext"
```

### 9. 카카오톡 대화방 파싱
```bash
python skills/kakao-chat-extractor/scripts/parse_kakao.py "카카오톡_대화내용.txt" --keyword "횡령" --output parsed.json
```

---

## 📄 라이선스 (License)
MIT License (c) 2026 daeryundf2-prog
