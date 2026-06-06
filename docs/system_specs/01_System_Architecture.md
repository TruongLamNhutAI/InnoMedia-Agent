# 01. System Architecture

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

## 3. Agent Architecture
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

## 4. Global Workflow

```text
Plaintext
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

## 5. Non-Negotiable Rules

- Không hallucinate product facts.
- Không bỏ qua Critic Agent trong workflow production.
- Không skip RAG khi RAG đã available.
- Không để Media Agent quyết định nội dung.
- Không dùng product data làm persistent RAG knowledge nếu chưa được tổng quát hóa.
- `video_plan` là source of truth cho render.
- Tối ưu conversion là ưu tiên số 1.


