---
name: kakao-chat-extractor
description: 카카오톡 모바일/PC 텍스트 내보내기(.txt) 파싱. SQLite·백업 DB·대화방 폴더 탐색에는 쓰지 말 것.
---

# kakao-chat-extractor: 카카오톡 텍스트 내보내기 파서

지원 포맷은 아래 두 가지뿐이다.

1. **모바일 텍스트 내보내기**
   - `--------------- 2024년 1월 16일 화요일 ---------------`
   - `[홍길동] [오후 2:15] 안녕하세요.`
   - 초 단위가 없어 시각은 `:00`으로 기록한다.
2. **PC 텍스트 내보내기**
   - `[2024-01-16 14:15:22] 홍길동: 안녕하세요.`

UTF-8, UTF-8 BOM, UTF-16 LE/BE를 시도한다.
모바일 메시지 앞에 날짜 헤더가 없으면 `timestamp`는 `null`, `timestamp_unknown`은 `true`다. 1970년 날짜를 만들지 않는다.
PC 발신자 이름의 콜론은 메시지 구분 콜론 뒤에 공백이 있는 표준 내보내기 형식에서만 보존된다.

## 하지 않는 일

- Android/iOS 백업, `chat_logs` SQLite, 암호화 DB
- 대화방 폴더 자동 탐색
- 실명·사건 당사자 예시 사용

## 실행

```bash
python skills/kakao-chat-extractor/scripts/parse_kakao.py "카카오톡_대화내용.txt" --keyword "키워드" --output parsed.json
```

## Antigravity / Gemini

파서는 `invoke_subagent` `Model: "flash"`. 모바일 시각은 초가 없어 `:00`이다. `view_file`을 만들지 말 것.
