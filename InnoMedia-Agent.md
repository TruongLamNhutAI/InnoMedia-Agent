# InnoMedia-Agent System Spec

## 1. System Overview

InnoMedia-Agent là một hệ thống Multi-Agent AI để tạo video affiliate marketing từ:

- Shopee/TikTok Shop product link
- ảnh sản phẩm
- mô tả sản phẩm
- instruction bổ sung từ user

Mục tiêu cuối cùng không phải là "tạo video đẹp", mà là tạo video ngắn cho TikTok/Reels/Shorts tối ưu:

- CTR
- conversion
- retention trong 3-5 giây đầu
- CTA rõ ràng
- khả năng học lại từ feedback/performance

Hệ thống nên được hiểu là:

> AI Marketing Production System

Không phải một model tạo video đơn lẻ.

## 2. Core Principles

- Product data là input tạm thời, không đưa vào RAG lâu dài.
- RAG là marketing knowledge base, lưu hook, CTA, scene pattern, visual style, failure case và performance signal.
- Agent phải có tool, memory, state và feedback loop.
- Media service không quyết định nội dung marketing.
- Critic Agent không được bỏ qua trong workflow production.
- Output chuẩn của Agent Orchestrator là `video_plan`, không phải chỉ là prompt rời rạc.

## 3. Target Input Contract

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

Phase 1 hiện tại vẫn có thể nhận `product_url` để tương thích với Django UI cũ, nhưng nội bộ cần chuẩn hóa dần sang input contract trên.

## 4. Agent Architecture

Pipeline chuẩn gồm các lớp sau:

```text
Director Agent
  |
  |-- Product Intelligence Layer
  |     |-- Product Agent
  |     |-- Vision Agent
  |
  |-- Marketing Intelligence Layer
  |     |-- RAG Retrieval Agent
  |     |-- Marketing Strategy Agent
  |
  |-- Creative Planning Layer
  |     |-- Script Agent
  |     |-- Critic Agent
  |     |-- Scene Planner Agent
  |     |-- Prompt Engineer Agent
  |     |-- Visual Director Agent
  |
  |-- Media Execution Layer
  |     |-- TTS
  |     |-- Image/Video Generation
  |     |-- Video Composer
  |
  |-- Learning Layer
        |-- Feedback Logger
        |-- RAG Knowledge Updater
```

## 5. Agent Responsibilities

### 5.1 Director Agent

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

### 5.2 Product Agent

Role: hiểu sản phẩm từ link, ảnh hoặc description.

Tools:

- scraper
- OCR
- vision model
- product parser

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
- nếu thiếu dữ liệu thì ghi rõ vào `risk_notes`

### 5.3 Vision Agent

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

### 5.4 RAG Retrieval Agent

Role: lấy tri thức marketing phù hợp từ vector DB.

Collections:

- `hook_patterns`
- `cta_patterns`
- `scene_patterns`
- `visual_styles`
- `audience_insights`
- `platform_rules`
- `failure_cases`
- `high_performing_examples`

Ranking:

```text
score = similarity * 0.6 + performance_score * 0.4
```

Rules:

- RAG không lưu product data cụ thể của từng job
- ưu tiên knowledge có cùng category, audience, platform
- trả về cả positive examples và failure cases nếu có

### 5.5 Marketing Strategy Agent

Role: chọn chiến lược bán hàng trước khi viết script.

Input:

- product data
- target audience
- platform
- RAG retrieved docs

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

### 5.6 Script Agent

Role: viết script marketing hoàn chỉnh.

Input:

- product data
- marketing strategy
- RAG examples
- platform constraints

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
- nếu dùng claim nhạy cảm, ghi vào `claims_used`
- không tạo image prompt

### 5.7 Critic Agent

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

- nếu `hook_score < 7`, quay lại Marketing Strategy Agent
- nếu `clarity_score < 7`, quay lại Script Agent
- nếu `platform_fit_score < 7`, quay lại Director Agent
- nếu quá retry limit, fail mềm hoặc trả best candidate có ghi risk

### 5.8 Scene Planner Agent

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

### 5.9 Prompt Engineer Agent

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

### 5.10 Visual Director Agent

Role: kiểm tra consistency trước khi render.

Checks:

- cùng sản phẩm
- cùng visual style
- prompt không mâu thuẫn
- không sinh chữ trong ảnh
- scene nào cũng có product/benefit focus phù hợp

Output:

```json
{
  "approved": true,
  "visual_consistency_score": 8.5,
  "fixed_prompts": []
}
```

### 5.11 Media Agent / Media Engine

Role: thực thi render.

Input chính:

- `video_plan`

Tools:

- TTS
- image generation
- optional image-to-video
- subtitle renderer
- FFmpeg/MoviePy composer

Rules:

- không thay đổi script
- không thay đổi marketing strategy
- chỉ render theo `video_plan`

## 6. Canonical Output: Video Plan

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

`data` chỉ là alias tạm thời cho frontend cũ chỉnh scene. Contract chính là `video_plan`.

## 7. Global Workflow

```text
Input Intake
  ↓
Director Agent
  ↓
Product Agent + Vision Agent
  ↓
RAG Retrieval Agent
  ↓
Marketing Strategy Agent
  ↓
Script Agent
  ↓
Critic Agent
  ↓ retry nếu fail
Scene Planner Agent
  ↓
Prompt Engineer Agent
  ↓
Visual Director Agent
  ↓ retry prompt nếu fail
Finalize Video Plan
  ↓
Media Engine
  ↓
Final Video
  ↓
Feedback / Learning Layer
```

## 8. Phase Roadmap

### Phase 1: Schema + Contract Standardization

Status: đang triển khai.

Goals:

- thêm Pydantic schema chuẩn
- Orchestrator trả `video_plan`
- Gateway lưu response mới vào `script_data`
- Media Engine nhận `video_plan`
- giữ backward compatibility với `data/scenes`

Không làm trong Phase 1:

- RAG thật
- scraper thật
- vision model thật
- learning loop thật

### Phase 2: Multi-Agent Workflow

Goals:

- tách node theo agent responsibilities
- thêm Director Agent thật
- thêm Critic routing chi tiết
- tách Script, Scene Planner, Prompt Engineer, Visual Director

### Phase 3: RAG Core

Goals:

- thêm vector DB
- seed marketing knowledge
- Marketing Agent query RAG
- ranking theo similarity + performance

### Phase 4: Product + Vision Intelligence

Goals:

- scraper/OCR/vision
- normalize product facts
- risk notes khi thiếu dữ liệu

### Phase 5: Feedback + Learning

Goals:

- lưu user edits
- lưu rerender count
- lưu performance nếu có
- cập nhật RAG có kiểm duyệt

## 9. Non-Negotiable Rules

- Không hallucinate product facts.
- Không bỏ qua Critic Agent trong workflow production.
- Không skip RAG khi RAG đã available.
- Không để Media Agent quyết định nội dung.
- Không dùng product data làm persistent RAG knowledge nếu chưa được tổng quát hóa.
- `video_plan` là source of truth cho render.
- Tối ưu conversion là ưu tiên số 1.

## 10. Context Cần Bổ Sung Từ User

Các điểm cần quyết định trước Phase 2/3:

- Nguồn dữ liệu performance ban đầu cho RAG: tự seed thủ công, lấy từ dataset có sẵn, hay log từ chính sản phẩm?
- Nền tảng ưu tiên đầu tiên: TikTok, Reels hay Shorts?
- Product source ưu tiên: Shopee, TikTok Shop, hay input ảnh/mô tả trước?
- Có cần crawl thật ở giai đoạn MVP không, hay bắt đầu bằng user-provided description/images?
- Voice/style mặc định: nữ Việt energetic, review tự nhiên, hay quảng cáo mạnh?
- Image/video model production mong muốn: Pollinations tạm thời, Flux/SDXL local, hay API trả phí?
