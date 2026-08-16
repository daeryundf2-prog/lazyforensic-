# 구현하지 않은 능력

이 목록은 광고와 구현의 차이를 고정한다. 이번 레인 작업에서 아래 파서를 만들지 않았다.

## DLP

`dlp-leakage-detector`는 분석관이 이미 확보한 로그를 맞추는 체크리스트다. 자동 유출 탐지 엔진이 없다.

다음 패스 후보: 사용자가 준 CSV를 표로 옮기는 보조(탐지 아님).

## 카카오톡

`kakao-chat-extractor`는 모바일/PC **텍스트 내보내기**만 읽는다. SQLite `chat_logs`나 백업 DB 파서는 없다.

## 파일시스템 고급 분석

`$MFT`, `$SI` vs `$FN`, Timestomping 판정, Maya, MOV `mvhd`는 없다. `forensic-audit`는 `os.stat`과 해시만 본다.

## Manim

`video-editor/manim-video/REFERENCE.md`는 참고 문서다. 교육 영상 렌더 파이프라인이 아니다.

## 법령 MCP

소스는 `korean-law-mcp/`에 있다. 빌드와 `LAW_OC`가 없으면 조회하지 않는다. 법률 자문 엔진이 아니다. 이 레포에서 `fly deploy`를 하지 않는다.

## 벤더 라이선스

`NOTICE`대로 `skills/slopslap/`와 `mengto-skills/`에는 라이선스 파일이 없다. `design-systems/`는 상표·브랜드 디자인 권리가 없다. 배포 전에 별도로 결정한다.
