---
name: legal-forensic-consult
description: 위임계약 서식 빈칸·법령/판례 조회 보조. 법률 자문·적법/위법 단정·조문 창작에는 쓰지 말 것.
---

# legal-forensic-consult: 서식·법령 조회 보조

계약서 초안 작성과 `korean_law` MCP를 통한 법령/판례 **조회**를 돕는다.

이 스킬은 법률 자문이 아니다. 적법성, 위법수집증거, 압수수색 대응을 결정하지 않는다.  
변호사 검토 없이 법원/수사기관에 제출할 의견서로 쓰지 않는다.

## 사용

- 위임 계약 서식 빈칸 채우기 (`templates/contract_template.md`)
- 법령명·조문·판례번호 조회 후 **원문 확인**
- 인용 검증 도구가 있으면 환각 조문을 걸러 보기

## 하지 않는 일

- "최신 판례에 따르면 적법/위법" 단정
- 주민등록번호 수집
- MCP가 빌드되지 않았거나 `LAW_OC`가 없을 때 조문을 지어내기

`korean_law`는 `korean-law-mcp/build/index.js`가 있을 때만 호출한다. 조회 결과는 `invoke_subagent` `Model: "pro"`로 원문과 대조한다.
