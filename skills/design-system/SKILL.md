---
name: design-system
description: 74개 이상의 글로벌 최고급 브랜드(Linear, Apple, Stripe, Vercel, Raycast, Supabase 등) DESIGN.md 명세를 기반으로 타임라인 뷰어, 포렌식 대시보드, 웹 리포트 및 인포그래픽에 프리미엄 UI/UX 디자인 시스템을 적용하는 스킬.
---

# design-system — 벤더 DESIGN.md 카탈로그

UI 토큰 참고용이다. 포렌식 엔진이 아니며, 브랜드 상표/디자인의 상업 재배포 권한을 보증하지 않는다.

이 스킬은 `design-systems/`의 `DESIGN.md` 토큰을 읽어 웹 화면 스타일을 맞출 때 쓴다.

---

## 🎨 주요 지원 디자인 시스템 (74개 브랜드 내장)

| 카테고리 | 대표 브랜드 DESIGN.md | 특징 및 최적 활용처 |
| :--- | :--- | :--- |
| **다크 엔지니어링 / 테크** | **`linear.app`**, **`raycast`**, **`warp`**, **`cursor`** | 고밀도 데이터, 다크 테마 타임라인 뷰어, 포렌식 아티팩트 로그 분석기 |
| **모던 미니멀 / 럭셔리** | **`apple`**, **`vercel`**, **`resend`**, **`framer`** | 법원/의뢰인 제출용 깔끔한 화이트/라이트 보고서 뷰어, 발표용 슬라이드 |
| **비즈니스 / 핀테크** | **`stripe`**, **`revolut`**, **`wise`**, **`coinbase`** | 포렌식 센터 수임/매출 통계 대시보드, 횡령/금융 거래 흐름도 |
| **데이터 / 대시보드** | **`supabase`**, **`posthog`**, **`sentry`**, **`clickhouse`** | 대량 이벤트 로그 분석 차트, KPI 위젯, DLP 유출 상관관계 매트릭스 |

---

## 🛠️ 디자인 토큰 적용 방법

디자인 명세는 `lazyforensic/design-systems/<brand>/DESIGN.md`에서 직접 로드하여 사용합니다.

### 1. CSS 변수(Variables) 주입 예시 (Linear 스타일 다크 테마)
```css
:root {
  --canvas: #010102;
  --surface-1: #0f1011;
  --surface-2: #141516;
  --hairline: #23252a;
  --primary: #5e6ad2;
  --primary-hover: #828fff;
  --ink: #f7f8f8;
  --ink-muted: #d0d6e0;
  --ink-subtle: #8a8f98;
  --font-display: -apple-system, BlinkMacSystemFont, "Pretendard", "Segoe UI", sans-serif;
}
```

### 2. AntV 인포그래픽 팔레트 연동
```infographic
infographic list-row-horizontal-icon-arrow
data
  title 디지털포렌식 분석 타임라인
  ...
theme
  palette #5e6ad2 #828fff #27a644 #f7f8f8
```

---

## 💡 활용 예시
- *"이 PC 사용기록 타임라인 HTML을 Linear 스타일 다크 테마로 세련되게 만들어줘"*
- *"포렌식 센터 7개월 매출 현황 대시보드를 Stripe 핀테크 스타일로 깔끔하게 디자인해줘"*
- *"법원 제출용 1페이지 인포그래픽을 Apple 미니멀 스타일로 렌더링해줘"*
