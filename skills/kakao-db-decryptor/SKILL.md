---
name: kakao-db-decryptor
description: "카카오톡 DB 래퍼 — 텍스트 내보내기만 지원, SQLite 복호화 미제공. 암호화 DB는 별도 도구 필요."
---

# KakaoTalk SQLite DB Decryptor & Extractor (래퍼 — 제한적)

> **현재 한계**: 이 플러그인은 **텍스트 내보내기(.txt)만** 파싱한다(`kakao-chat-extractor`). 암호화된 SQLite(`KakaoTalk.db`, `EvaSQLite`, `chat_data.db`) **복호화는 제공하지 않는다**. `kakaodecrypt.py`는 예시일 뿐 번들로 포함되지 않는다. SQLite 파싱이 필요하면 별도 포렌식 도구와 키를 확보해야 한다.

## 지원하는 것 — 텍스트 내보내기만
- `skills/kakao-chat-extractor`의 `parse_kakao.py`로 모바일/PC 텍스트 내보내기 파싱
- `events.json` → `forensic-timeline` HTML 변환은 가능

## 지원하지 않는 것 (docs/GAPS.md)
- Android/iOS 백업, `chat_logs` SQLite, SQLCipher 복호화
- `kakaodecrypt.py` 자동 실행 (파일 없음 — 예시 경로)
- 대화방 폴더 자동 탐색

## 참고 (별도 도구 — 미포함)
- 복호화된 DB가 있다면 예시 쿼리:
  ```sql
  SELECT datetime(created_at / 1000, 'unixepoch', 'localtime') AS timestamp,
         type, user_id, message
  FROM chat_logs
  ORDER BY created_at ASC;
  ```
- 주의: KakaoTalk `chat_logs.created_at`은 epoch **밀리초**다 — `/ 1000` 없이 `unixepoch`에 넘기면 날짜가 전부 틀어진다.
- 이 결과는 `forensic-timeline`의 `events.json`으로 수동 변환해야 한다. 자동 변환기는 제공하지 않는다.
