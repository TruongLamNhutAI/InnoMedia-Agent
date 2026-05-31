import os
import requests
from celery import shared_task
from django.conf import settings
from .models import VideoProject

# Đường dẫn gọi tới các service (Kiểm tra kỹ và đảm bảo đúng cổng)
SERVICE_2_URL = "http://host.docker.internal:8000/api/v1/generate" # Đổi cổng nếu Service 2 dùng cổng khác
SERVICE_3_URL = "http://localhost:8001/api/v1/render"

@shared_task
def process_video_pipeline(project_id: str, url: str):
    try:
        project = VideoProject.objects.get(id=project_id)
        project.status = 'PROCESSING'
        project.save()
        
        # --- BƯỚC 1: GỌI SERVICE 2 (AI ORCHESTRATOR) ---
        print(f"[Celery] Gọi Service 2 để phân tích kịch bản...")
        
        # 1. Gọi đúng cổng 8002 và đúng Endpoint
        service2_endpoint = "http://localhost:8002/api/v1/generate-script"
        
        # 2. Gửi đúng từ khóa "product_url"
        resp_2 = requests.post(service2_endpoint, json={"product_url": url}, timeout=120) 
        
        resp_2.raise_for_status()
        script_data = resp_2.json()
        print("   -> Đã nhận kịch bản AI!")

        # --- BƯỚC 2: GỌI SERVICE 3 (MEDIA ENGINE) ---
        print(f"[Celery] Gọi Service 3 để bắt đầu Render Video...")
        
        # 3. Lấy dữ liệu từ hộp "data" thay vì "scenes"
        scenes_list = script_data.get("data", [])
        
        resp_3 = requests.post(SERVICE_3_URL, json={"scenes": scenes_list}, timeout=600)
        resp_3.raise_for_status() 
        print("   -> Render xong! Đang tải file MP4 về...")

        # --- BƯỚC 3: LƯU FILE VIDEO VÀO DJANGO ---
        # Đảm bảo thư mục media/ đã tồn tại
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        
        file_name = f"InnoMedia_{project_id[:8]}.mp4"
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)
        
        # Ghi từng byte (chunk) của file video xuống ổ cứng
        with open(file_path, 'wb') as f:
            for chunk in resp_3.iter_content(chunk_size=8192):
                f.write(chunk)
                
        # --- BƯỚC 4: HOÀN TẤT ---
        project.status = 'SUCCESS'
        project.final_video_path = f'/media/{file_name}'
        project.save()
        
        print(f"[Celery] 🎉 HOÀN TẤT THỰC SỰ! Video đã lưu tại: {file_path}\n")
        return "SUCCESS"
        
    except requests.exceptions.RequestException as req_err:
        error_msg = f"Lỗi gọi Service: {str(req_err)}"
        project.status = 'FAILED'
        project.error_message = error_msg
        project.save()
        print(f"\n[Celery] ❌ {error_msg}\n")
        return "FAILED"
    except Exception as e:
        project.status = 'FAILED'
        project.error_message = str(e)
        project.save()
        print(f"\n[Celery] ❌ LỖI HỆ THỐNG: {str(e)}\n")
        return "FAILED"