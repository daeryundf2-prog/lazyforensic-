---
name: infographic-creator
description: 포렌식 절차/유출경로 인포그래픽이 필요할 때만. AntV DSL은 vendor를 한 파일만 Read. 감정·법령·카카오 파싱에는 쓰지 말 것.
---

# infographic-creator

한국어 요청이면 제목/라벨을 한국어로 둔다. 중국어 원문을 사용자에게 따라가지 않는다.

1. 데이터(숫자·단계)가 없으면 그리지 않는다.
2. AntV 문법이 필요하면 `vendor/antv-infographic/INDEX.md`를 읽고 표에서 **하나만** Read 한다. 기본은 `creator-full.md`.
3. 검토한 로컬 AntV 번들과 입력 파일을 명시해 렌더한다:
   `python skills/infographic-creator/scripts/render_infographic.py chart.infographic --antv-script "<검토한_로컬_번들.js>" --output chart.html`
4. 위성 스킬은 INDEX에만 있다. `skills/` 피커와 `vendor/` glob에 올리지 않는다.

`invoke_subagent` `Model: "flash"`로 DSL을 만들고, 부모는 렌더 스크립트만 실행한다.
입력이나 `--antv-script`가 없으면 종료한다. 샘플 감정 절차나 `@latest` CDN을 자동 삽입하지 않는다.
