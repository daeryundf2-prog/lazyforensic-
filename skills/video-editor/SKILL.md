---
name: video-editor
description: 동영상 구간 자르기·필름스트립/파형. 원본은 수정하지 않는다. 법원 제출본·Manim 교육영상에는 쓰지 말 것.
---

# video-editor

원본은 그대로 두고 `_extracted` / `_enhanced` 사본만 만든다.

```bash
python skills/video-editor/helpers/timeline_view.py "<동영상경로>" <시작초> <종료초> -o timeline_strip.png --n-frames 12
python skills/video-editor/helpers/render.py edl.json -o extracted_clip.mp4 --build-subtitles
```

Manim 참고는 `manim-video/REFERENCE.md`다. 스킬 카탈로그에 올리지 않는다.

가공 이력(구간, 필터)을 보고서에 적는다. `invoke_subagent` `Model: "flash"`로 클립을 만들고 부모는 원본 경로가 그대로인지 확인한다.
