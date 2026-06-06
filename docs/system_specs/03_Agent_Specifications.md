# 03. Agent Specifications

## 1. Director Agent
Role: điều phối toàn bộ pipeline.
Responsibilities:
- phân tích input user
- xác định video goal
- xác định workflow cần chạy
- quyết định có cần scraping, vision, RAG hay không
- route retry khi Critic reject

Output:
```json
{
  "need_scraping": true,
  "need_vision_analysis": true,
  "need_rag": true,
  "video_goal": "conversion",
  "workflow_type": "affiliate_review",
  "target_platform": "tiktok",
  "expected_duration": 30
}
```

Rules:

- không viết script
- không tạo media prompt
- không tự bịa product fact
- chỉ lập kế hoạch và route state

## 2. Product Agent
Role: hiểu sản phẩm từ link, ảnh hoặc description.
Tools: scraper, OCR, vision model, product parser.
Output:
```json
{
  "name": "",
  "category": "",
  "brand": "",
  "price": "",
  "description": "",
  "selling_points": [],
  "pain_points": [],
  "reviews_summary": [],
  "risk_notes": []
}
```

Rules:

- chỉ extract và normalize
- không sáng tạo thông tin sản phẩm
- nếu thiếu dữ liệu thì ghi rõ vào risk_notes

## 3. Vision Agent
Role: phân tích ảnh sản phẩm.
Output:
```json
{
  "visual_attributes": [],
  "dominant_colors": [],
  "product_style": "minimal | tech | luxury | cute",
  "recommended_visual_direction": ""
}
```

Rules:

- không tạo prompt render
- chỉ mô tả visual facts và style suggestion

## 4. RAG Retrieval Agent
Role: lấy tri thức marketing phù hợp từ vector DB.
Collections: hook_patterns, cta_patterns, scene_patterns, visual_styles, audience_insights, platform_rules, failure_cases, high_performing_examples.
Ranking: score = similarity * 0.6 + performance_score * 0.4
Rules:

- RAG không lưu product data cụ thể của từng job
- ưu tiên knowledge có cùng category, audience, platform
- trả về cả positive examples và failure cases nếu có

## 5. Marketing Strategy Agent
Role: chọn chiến lược bán hàng trước khi viết script.
Input: product data, target audience, platform, RAG retrieved docs.
Output:
```json
{
  "video_goal": "conversion",
  "hook_strategy": "pain_point",
  "story_structure": "hook -> problem -> demo -> benefit -> CTA",
  "selected_hooks": [],
  "selected_ctas": [],
  "visual_style": "clean product demo",
  "persuasion_angle": "save time",
  "avoid": []
}
```

Rules:

- luôn ưu tiên hook có evidence từ RAG
- không copy product description thành hook
- tối ưu 3 giây đầu

## 6. Script Agent
Role: viết script marketing hoàn chỉnh.
Input: product data, marketing strategy, RAG examples, platform constraints.
Output:
```json
{
  "hook": "",
  "body": "",
  "cta": "",
  "full_script": "",
  "estimated_duration": 30,
  "claims_used": []
}
```

Rules:

- chỉ dùng product facts đã có
- nếu dùng claim nhạy cảm, ghi vào claims_used
- không tạo image prompt

## 7. Critic Agent
Role: đánh giá chất lượng marketing.
Output:
```json
{
  "approved": true,
  "overall_score": 8.4,
  "hook_score": 8.8,
  "clarity_score": 8.0,
  "conversion_score": 8.5,
  "platform_fit_score": 8.2,
  "issues": [],
  "revision_instruction": ""
}
```

Routing:

- nếu hook_score < 7, quay lại Marketing Strategy Agent
- nếu clarity_score < 7, quay lại Script Agent
- nếu platform_fit_score < 7, quay lại Director Agent
- nếu quá retry limit, fail mềm hoặc trả best candidate có ghi risk

## 8. Scene Planner Agent
Role: chia script thành scenes.
Output:
```json
{
  "scenes": [
    {
      "scene_number": 1,
      "duration": 4,
      "voiceover_text": "",
      "subtitle_text": "",
      "scene_goal": "hook",
      "visual_description": "",
      "product_focus": true,
      "transition": "cut"
    }
  ]
}
```

Rules:

- không viết image prompt chi tiết
- mỗi scene phải có mục tiêu rõ ràng
- duration phải khớp tốc độ đọc tiếng Việt

## 9. Prompt Engineer Agent
Role: chuyển scene plan thành prompt cho image/video model.
Output:
```json
{
  "scenes": [
    {
      "scene_number": 1,
      "image_prompt": "",
      "negative_prompt": "",
      "camera": "",
      "lighting": "",
      "style_tags": [],
      "consistency_notes": ""
    }
  ]
}
```

Rules:

- prompt bằng tiếng Anh
- không yêu cầu text trong ảnh
- giữ style nhất quán giữa các scene
- ưu tiên vertical 9:16 cho TikTok/Reels/Shorts

## 10. Visual Director Agent
Role: kiểm tra consistency trước khi render.
Checks:

cùng sản phẩm, cùng visual style, prompt không mâu thuẫn

không sinh chữ trong ảnh

scene nào cũng có product/benefit focus phù hợp
Output:

```json
{
  "approved": true,
  "visual_consistency_score": 8.5,
  "fixed_prompts": []
}
```

## 11. Media Agent / Media Engine
Role: thực thi render.
Input chính: video_plan
Tools: TTS, image generation, optional image-to-video, subtitle renderer, FFmpeg/MoviePy composer.
Rules:

- không thay đổi script
- không thay đổi marketing strategy
- chỉ render theo video_plan