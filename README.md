Markdown
# 🎬 InnoMedia-Agent: Automated AI Video Affiliate Pipeline

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![Django](https://img.shields.io/badge/Django-Web_Gateway-092E20?style=for-the-badge&logo=django)
![FastAPI](https://img.shields.io/badge/FastAPI-Media_Engine-009688?style=for-the-badge&logo=fastapi)
![Celery](https://img.shields.io/badge/Celery-Task_Queue-37814A?style=for-the-badge&logo=celery)
![Redis](https://img.shields.io/badge/Redis-Message_Broker-DC382D?style=for-the-badge&logo=redis)
![Docker](https://img.shields.io/badge/Docker-Containerization-2496ED?style=for-the-badge&logo=docker)

## 📖 Overview
**InnoMedia-Agent** is a fully automated pipeline designed for the production of Affiliate Marketing videos. Starting from a single e-commerce product URL, the system leverages a robust **Microservices** architecture to extract information, utilizes AI (LangGraph) to generate highly-converting sales scripts, and finally renders a complete video (including AI-generated images, Text-to-Speech voiceovers, dynamic subtitles, and background music) ready for publication.

The project is built with a Production-ready mindset, emphasizing Asynchronous Processing, Fault Tolerance, and complete environment isolation via Docker.

## 🏗️ System Architecture
The pipeline is divided into 5 independent services communicating via a Message Broker:

1. **Service 1: Web Gateway (Django)**
   - Acts as the User Interface (UI) and primary entry point.
   - Receives product URLs, logs task status into the Database, and dispatches jobs to the queue.
2. **Message Broker (Redis)**
   - The central data hub, maintaining the task queue to prevent system overload during high-traffic spikes.
3. **Task Worker (Celery)**
   - Operates as a background processor. Retrieves tasks from Redis, orchestrates API calls between the AI and Media services, and manages final asset storage.
4. **Service 2: AI Orchestrator (FastAPI + LangGraph + Groq)**
   - Analyzes the product URL and utilizes a Multi-Agent system (e.g., a 'Writer' and a 'Reviewer' collaborating and self-correcting) to craft the most effective sales script.
5. **Service 3: Media Engine (FastAPI + Docker + FFMPEG)**
   - The "Render Factory," completely containerized to handle complex dependencies (MoviePy, ImageMagick).
   - Automatically orchestrates API calls for Image Generation (Pollinations AI) and TTS (Edge-TTS), then utilizes core FFMPEG to composite audio, subtitles, and video efficiently. Implements Semaphore-based rate-limiting to ensure API stability.

## 🚀 Key Technical Features
* **Asynchronous Execution & Queueing:** Users experience a non-blocking UI during the video rendering process, thanks to the Celery + Redis architecture.
* **Concurrency Control & Exponential Backoff:** Implements `asyncio.Semaphore` and Backoff Retry algorithms within the Media Engine to prevent `429 Too Many Requests` errors when calling external generative APIs.
* **Fault Tolerance:** If a specific scene fails to fetch resources (e.g., image API timeout), the system gracefully skips the failed asset and continues rendering the remaining scenes, ensuring a final output is always delivered rather than crashing the pipeline.
* **Automated Garbage Collection:** Integrates a cleanup mechanism to immediately purge temporary assets (images, audio files) after successful FFMPEG rendering, optimizing server storage capacity.

## 🛠️ Tech Stack
* **Backend Frameworks:** Python, Django, FastAPI, Celery
* **Infrastructure & DevOps:** Docker, Redis, WSL2 (Ubuntu)
* **AI & LLMs:** LangGraph, LangChain, Groq (Llama-3), Pollinations AI, Edge-TTS
* **Media Processing:** FFMPEG CLI, MoviePy, ImageMagick

## ⚙️ Local Setup & Deployment Guide

### 1. Initialize Message Broker & Media Engine (Docker)
```bash
# Start Redis
docker run -d -p 6379:6379 --name redis-server redis:alpine

# Build and run the Media Engine (Port 8001)
cd media_engine
docker build -t innomedia-media-engine .
docker run -d -p 8001:8001 --name media-engine-container innomedia-media-engine
```

2. Initialize AI Orchestrator (Port 8002)
```Bash
cd agent_orchestrator
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8002
```

3. Start Celery Worker
``` Bash
cd web_gateway
source venv/bin/activate
# Limit concurrency to 2 to optimize RAM usage on local machines
python -m celery -A core.celery worker --concurrency=2 --loglevel=info
```

4. Start Web Gateway (Port 8000)
```Bash
cd web_gateway
source venv/bin/activate
python manage.py runserver
Navigate to http://127.0.0.1:8000 to interact with the application.
```
