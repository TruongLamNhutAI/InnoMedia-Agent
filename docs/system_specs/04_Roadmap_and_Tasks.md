# 04. Roadmap and Tasks

## 1. Phase Roadmap

### Phase 1: Schema + Contract Standardization
Status: đang triển khai.
Goals:
- thêm Pydantic schema chuẩn
- Orchestrator trả `video_plan`
- Gateway lưu response mới vào `script_data`
- Media Engine nhận `video_plan`
- giữ backward compatibility với `data/scenes`
Không làm trong Phase 1: RAG thật, scraper thật, vision model thật, learning loop thật.

### Phase 2: Multi-Agent Workflow
Goals:
- tách node theo agent responsibilities (refactor thành Class)
- thêm Director Agent để phân tích và định tuyến luồng chạy
- thêm Critic routing chi tiết
- tách bạch các module: Script, Scene Planner, Prompt Engineer, Visual Director

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
- lưu user edits, lưu rerender count
- lưu performance nếu có
- cập nhật RAG có kiểm duyệt

## 2. Context Cần Bổ Sung Từ User (Quyết định kiến trúc Phase 2/3)

Dựa trên quá trình phân tích và đóng gói MVP, các thiết lập dưới đây được chốt để định hướng thiết kế hệ thống cho Phase 2 và Phase 3:

- **Nguồn dữ liệu performance ban đầu cho RAG:** Tự seed thủ công. Khởi đầu với 20-30 mẫu hook/CTA tĩnh (việc tự động hóa log từ sản phẩm sẽ làm ở Phase 5).
- **Nền tảng ưu tiên đầu tiên:** TikTok (tối ưu cho 30s, 9:16, 3-5 giây đầu).
- **Product source ưu tiên:** Shopee, TikTok Shop, hoặc input ảnh/mô tả trước bằng tay. Chưa bắt buộc crawl thật toàn diện ở MVP.
- **Voice/style mặc định:** Nữ Việt năng động (energetic), phong cách review tự nhiên.
- **Image/video model production mong muốn:** Tiếp tục dùng Pollinations tạm thời để ổn định luồng chạy.
- **Mô hình LLM:** Dùng `gpt-4o-mini` cho Director/Critic (cần logic cao, JSON chuẩn xác). Dùng `Groq (Llama-3.3-70b)` cho Script/Prompt Engineer (cần tốc độ và khối lượng text lớn).