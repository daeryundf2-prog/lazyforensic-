# LazyForensic

> **Digital Forensic & Incident Response (DFIR) Specialist Suite for Google Antigravity**  
> 법무법인(유한) 대륜 디지털포렌식센터 맞춤형 디지털 포렌식·감정보고서·아티팩트 분석 독립 플러그인

---

## 🌟 개요 (Overview)

`LazyForensic`은 Google Antigravity 에이전트 환경에서 동작하는 전문 디지털 포렌식 확장 플러그인입니다.  
개발·코딩용 플러그인(`LazyAntigravity`)과 완전히 분리되어 독립적으로 동작하며, 법원/수사기관 제출용 포렌식 감정보고서 작성, 시계열 타임라인 자동 생성, 파일 타임스탬프 위변조 감정, 모바일/카카오톡 대화 분석, DLP 정보유출 교차 분석을 자동화합니다.

---

## 🛠️ 핵심 스킬 구성 (Included Skills)

| 스킬명 | 설명 | 주요 실행 스크립트 |
| :--- | :--- | :--- |
| **`forensic-timeline`** | PC 사용기록, $MFT, 이벤트 로그를 결합한 인터랙티브 HTML 타임라인 및 인쇄용 PDF 자동 생성 | `scripts/generate_timeline.py` |
| **`forensic-audit`** | 파일 타임스탬프($SI vs $FN), 생성일시>수정일시 역전, 미디어/Maya 메타데이터 위변조 과학수사 감정 | `scripts/audit_timestamps.py` |
| **`forensic-report`** | 법무법인 대륜 디지털포렌식센터 표준 서식 기반 공식 감정서, 기술자문 의견서 작성 및 감수 | `templates/forensic_report_template.md` |
| **`kakao-chat-extractor`** | 대용량 카카오톡/모바일 대화방 텍스트 및 DB 파싱, 특정 인물·일자·키워드 대화 추출 | `scripts/parse_kakao.py` |
| **`dlp-leakage-detector`** | 기업 내부정보 유출 시 DLP 로그, 구글 검색어, USB 연결 기록을 결합한 유출 타임라인 산출 | - |
| **`legal-forensic-consult`** | 포렌식 위임 계약서, 보수기준표 기반 견적, 회사 PC 임의조사/압수수색 참관 관련 판례 자문 | `templates/contract_template.md` |

---

## 📂 디렉토리 구조 (Directory Structure)

```text
lazyforensic/
├── plugin.json                 # 플러그인 매니페스트 (Antigravity 자동 등록)
├── README.md                   # 프로젝트 문서
├── .gitignore                  # Git 관리 제외 규칙
├── templates/                  # 법원/의뢰인 제출 표준 서식
│   ├── forensic_report_template.md  # 포렌식 감정의견서 템플릿
│   └── contract_template.md         # 디지털포렌식 위임계약서 서식
└── skills/
    ├── forensic-timeline/      # 타임라인 생성 스킬
    ├── forensic-audit/         # 타임스탬프 감정 스킬
    ├── forensic-report/        # 감정보고서 작성 스킬
    ├── kakao-chat-extractor/   # 카카오톡/메신저 파싱 스킬
    ├── dlp-leakage-detector/   # DLP/유출 분석 스킬
    └── legal-forensic-consult/ # 포렌식 법률/계약 자문 스킬
```

---

## 🚀 빠른 시작 (Quick Start)

### 1. 시계열 타임라인 생성
```bash
python skills/forensic-timeline/scripts/generate_timeline.py --title "2024-01-16 PC 사용기록 전수 타임라인" --output timeline.html
```

### 2. 파일 타임스탬프 & 무결성 감정
```bash
python skills/forensic-audit/scripts/audit_timestamps.py "C:\경로\피분석파일.ext"
```

### 3. 카카오톡 대화방 파싱
```bash
python skills/kakao-chat-extractor/scripts/parse_kakao.py "카카오톡_대화내용.txt" --keyword "횡령" --output parsed.json
```

---

## 📄 라이선스 (License)
MIT License (c) 2026 daeryundf2-prog
