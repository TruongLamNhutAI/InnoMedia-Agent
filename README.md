Markdown
# 🎬 InnoMedia-Agent: Automated AI Video Affiliate Pipeline

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![Django](https://img.shields.io/badge/Django-Web_Gateway-092E20?style=for-the-badge&logo=django)
![FastAPI](https://img.shields.io/badge/FastAPI-Media_Engine-009688?style=for-the-badge&logo=fastapi)
![Celery](https://img.shields.io/badge/Celery-Task_Queue-37814A?style=for-the-badge&logo=celery)
![Redis](https://img.shields.io/badge/Redis-Message_Broker-DC382D?style=for-the-badge&logo=redis)
![Docker](https://img.shields.io/badge/Docker-Containerization-2496ED?style=for-the-badge&logo=docker)

## 📖 Tổng quan dự án (Overview)
**InnoMedia-Agent** là một hệ thống tự động hóa hoàn toàn quy trình sản xuất video Affiliate Marketing. Bắt đầu từ một đường link sản phẩm (E-commerce URL), hệ thống sử dụng kiến trúc **Microservices** để bóc tách thông tin, sử dụng AI (LangGraph) để tự động viết kịch bản chốt sale, và cuối cùng render ra một video hoàn chỉnh (bao gồm Hình ảnh, Giọng nói AI, Phụ đề và Nhạc nền) sẵn sàng để đăng tải.

Dự án được thiết kế hướng tới môi trường Production với khả năng xử lý bất đồng bộ (Asynchronous Processing), chịu lỗi cao (Fault Tolerance) và cách ly môi trường hoàn toàn bằng Docker.

## 🏗️ Kiến trúc Hệ thống (System Architecture)
Hệ thống được chia thành 5 thành phần (Services) hoạt động độc lập và giao tiếp thông qua Message Broker:

1. **Service 1: Web Gateway (Django)**
   - Đóng vai trò là điểm chạm của người dùng (User Interface).
   - Tiếp nhận URL sản phẩm, ghi nhận trạng thái vào Database và đẩy Task vào hàng đợi.
2. **Message Broker (Redis)**
   - Trạm trung chuyển dữ liệu trung tâm, lưu trữ hàng đợi công việc (Queue) để tránh quá tải hệ thống khi có nhiều yêu cầu cùng lúc.
3. **Task Worker (Celery)**
   - Chạy ngầm phía sau (Background Processing). Lấy Task từ Redis, điều phối luồng gọi API đến các AI Service và Media Service, sau đó lưu file kết quả.
4. **Service 2: AI Orchestrator (FastAPI + LangGraph + Groq)**
   - Phân tích URL sản phẩm. Sử dụng mô hình Multi-Agent (Writer & Reviewer cãi nhau để tự tối ưu kịch bản) nhằm tạo ra nội dung có tỷ lệ chuyển đổi cao nhất.
5. **Service 3: Media Engine (FastAPI + Docker + FFMPEG)**
   - "Xưởng dựng phim" được đóng gói hoàn toàn trong Docker để xử lý các thư viện phức tạp (MoviePy, ImageMagick).
   - Tự động gọi API tạo ảnh (Pollinations), sinh giọng nói (Edge-TTS) và dùng FFMPEG lõi ghép nối âm thanh, phụ đề với hiệu suất cao. Tích hợp cơ chế Semaphore để kiểm soát luồng (Rate-limiting).

## 🚀 Tính năng Kỹ thuật Nổi bật (Technical Highlights)
* **Asynchronous & Queueing:** Người dùng không bị treo trình duyệt (block) khi chờ render video nhờ kiến trúc Celery + Redis.
* **Concurrency Control & Exponential Backoff:** Áp dụng `asyncio.Semaphore` và thuật toán Backoff Retry trong Media Engine để tránh lỗi `429 Too Many Requests` khi gọi API sinh ảnh/âm thanh liên tục.
* **Fault Tolerance:** Nếu một phân cảnh (scene) bị lỗi tải tài nguyên, hệ thống vẫn tiếp tục dựng các cảnh còn lại và xuất ra video cuối cùng thay vì sập toàn bộ tiến trình.
* **Automated Garbage Collection:** Tích hợp cơ chế dọn dẹp nguyên liệu nháp ngay sau khi FFMPEG xuất xưởng thành công để tối ưu dung lượng máy chủ.

## 🛠️ Công nghệ sử dụng (Tech Stack)
* **Backend:** Python, Django, FastAPI, Celery
* **Infra & DevOps:** Docker, Redis, WSL2 (Ubuntu)
* **AI & LLM:** LangGraph, LangChain, Groq (Llama-3), Pollinations AI, Edge-TTS
* **Media Processing:** FFMPEG CLI, MoviePy, ImageMagick

## ⚙️ Hướng dẫn Cài đặt & Vận hành (Local Setup)

### 1. Khởi động Message Broker và Media Engine (Docker)
```bash
# Khởi động Redis
docker run -d -p 6379:6379 --name redis-server redis:alpine

# Build và chạy Media Engine (Cổng 8001)
cd media_engine
docker build -t innomedia-media-engine .
docker run -d -p 8001:8001 --name media-engine-container innomedia-media-engine
2. Khởi động AI Orchestrator (Cổng 8002)
Bash
cd agent_orchestrator
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8002
3. Khởi động Celery Worker
Bash
cd web_gateway
source venv/bin/activate
python -m celery -A core.celery worker --concurrency=2 --loglevel=info
4. Khởi động Web Gateway (Cổng 8000)
Bash
cd web_gateway
source venv/bin/activate
python manage.py runserver
Truy cập http://127.0.0.1:8000 để bắt đầu trải nghiệm hệ thống.
