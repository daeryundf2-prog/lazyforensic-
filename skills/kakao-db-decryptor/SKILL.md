---
name: kakao-db-decryptor
description: "카카오톡 암호화 SQLite DB(KakaoTalk.db / EvaSQLite) 복호화 및 대화방/메시지/첨부파일 포렌식 테이블 추출 스킬. Triggers: 카카오톡 db 복호화, kakaotalk.db, kakaodecrypt, 카카오 db 파싱."
---

# KakaoTalk SQLite DB Decryptor & Extractor

모바일(Android) 및 PC 윈도우 환경에서 추출된 암호화 카카오톡 SQLite 데이터베이스(`KakaoTalk.db`, `chat_data.db`)를 사용자 식별키 및 SQLCipher 파라미터를 통해 복호화하고, `chat_logs`, `chat_rooms`, `friends` 테이블을 포렌식 타임라인 데이터로 변환합니다.

## 핵심 도구 & 방법론

1. **Android `KakaoTalk.db` 복호화 (`kakaodecrypt`):**
   ```bash
   # 사용자 ID 추정 및 DB 복호화
   python scripts/kakaodecrypt.py --db "KakaoTalk.db" --output "decrypted_kakao.db"
   ```

2. **포렌식 타임라인 연동:**
   - 복호화된 SQLite 파일의 `chat_logs` 테이블 쿼리:
     ```sql
     SELECT datetime(created_at, 'unixepoch', 'localtime') AS timestamp,
            user_id, message, attachment
     FROM chat_logs
     ORDER BY created_at ASC;
     ```
   - 추출된 데이터를 `skills/forensic-timeline`의 `events.json` 포맷으로 변환하여 대화형 HTML 타임라인 생성.
