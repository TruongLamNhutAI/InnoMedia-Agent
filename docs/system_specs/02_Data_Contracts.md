# 02. Data Contracts

## 1. Target Input Contract

```json
{
  "product_link": "",
  "product_images": [],
  "custom_images": [],
  "product_description": "",
  "target_audience": "student | office | general",
  "platform": "tiktok",
  "video_duration": 30,
  "video_style": "review | ads | storytelling",
  "language": "vi",
  "tone": "funny | serious | luxury | energetic",
  "extra_instruction": ""
}
```

Phase 1 hiện tại vẫn có thể nhận product_url để tương thích với Django UI cũ, nhưng nội bộ cần chuẩn hóa dần sang input contract trên.

2. Canonical Output: Video Plan
Agent Orchestrator phải trả về:

```json
{
  "status": "success",
  "message": "Video Plan đã được tạo thành công.",
  "video_plan": {
    "project_id": "",
    "platform": "tiktok",
    "aspect_ratio": "9:16",
    "duration": 30,
    "language": "vi",
    "video_goal": "conversion",
    "product": {},
    "marketing_strategy": {},
    "script": {},
    "scenes": [
      {
        "scene_number": 1,
        "duration": 4,
        "voiceover_text": "",
        "subtitle_text": "",
        "scene_goal": "hook",
        "visual_description": "",
        "image_prompt": "",
        "visual_prompt": "",
        "negative_prompt": "",
        "visual_style": "",
        "camera": "",
        "transition": "cut"
      }
    ],
    "music": {
      "style": "lofi",
      "volume": 0.3
    },
    "quality_checks": {
      "script_score": 8.4,
      "visual_consistency_score": 8.5
    },
    "metadata": {
      "contract_version": "video_plan.v1"
    }
  },
  "data": []
}
```

data chỉ là alias tạm thời cho frontend cũ chỉnh scene. Contract chính là video_plan.