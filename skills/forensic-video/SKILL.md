---
name: forensic-video
description: CCTV/블랙박스 프레임 추출·ffprobe 태그. ffmpeg 필요. 촬영일시 조작의 법정 증명에는 쓰지 말 것.
---

# forensic-video

프레임을 뽑고 컨테이너 태그를 읽는다. 촬영 시점을 확정하지 않는다.

## 실행

```bash
python skills/forensic-video/scripts/setup.py --check
python skills/forensic-video/scripts/watch.py "<동영상경로>" --resolution 720
python skills/forensic-video/scripts/forensic_video_audit.py "<동영상경로>"
```

## Antigravity / Gemini

추출된 프레임은 호스트 `Read`로 본다. `view_file`을 만들지 말 것.
해석은 `invoke_subagent` `Model: "flash"`, 태그 vs `os.stat` 대조는 `Model: "pro"`.
번호판·신원 단정, 편집 여부 확정을 쓰지 않는다.
