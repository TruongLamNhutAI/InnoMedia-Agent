import os
import requests
from celery import shared_task
from django.conf import settings
from .models import VideoProject

# --- ĐỊNH NGHĨA ROUTING TRONG MẠNG DOCKER ---
SERVICE_2_URL = "http://agent_orchestrator:8002/api/v1/generate-script"
SERVICE_3_URL = "http://media_engine:8001/api/v1/render"


def build_video_plan_payload(script_data: dict) -> dict:
    """
    Normalize old and new orchestrator contracts into the Media Engine payload.
    Phase 1 keeps `data` as an editable scene alias while making `video_plan`
    the primary contract.
    """
    if not isinstance(script_data, dict):
        raise ValueError("Dữ liệu kịch bản không hợp lệ.")

    editable_scenes = script_data.get("data") or []
    video_plan = script_data.get("video_plan") or {}

    if video_plan:
        video_plan = dict(video_plan)
        if editable_scenes:
            video_plan["scenes"] = editable_scenes
        return {"video_plan": video_plan}

    if editable_scenes:
        return {"scenes": editable_scenes}

    raise ValueError("Không tìm thấy scenes hoặc video_plan để render.")


@shared_task(bind=True)
def process_video_pipeline(self, project_id: str, url: str):
    project = None
    try:
        project = VideoProject.objects.get(id=project_id)
        project.status = 'PROCESSING'
        project.save()
        
        # --- BƯỚC 1: BÁO CÁO 10% ---
        self.update_state(state='PROGRESS', meta={'percent': 10, 'message': 'Đang phân tích URL và viết kịch bản AI...'})
        print(f"[Celery] Gọi Service 2 để phân tích kịch bản...")
        
        resp_2 = requests.post(SERVICE_2_URL, json={"product_url": url}, timeout=120) 
        resp_2.raise_for_status()
        script_data = resp_2.json()
        print("   -> Đã nhận kịch bản AI!")

        # --- CELERY LƯU KỊCH BẢN VÀO DATABASE ---
        project.script_data = script_data
        project.save()

        # --- BƯỚC 2: BÁO CÁO 40% ---
        self.update_state(state='PROGRESS', meta={'percent': 40, 'message': 'Đang gọi xưởng phim: Tạo hình ảnh & Giọng nói AI...'})
        print(f"[Celery] Gọi Service 3 để bắt đầu Render Video...")
        
        render_payload = build_video_plan_payload(script_data)
        
        resp_3 = requests.post(SERVICE_3_URL, json=render_payload, timeout=600)
        resp_3.raise_for_status() 
        print("   -> Render xong! Đang tải file MP4 về...")

        # --- BƯỚC 3: BÁO CÁO 90% ---
        self.update_state(state='PROGRESS', meta={'percent': 90, 'message': 'Đang đóng gói và lưu trữ Video...'})
        
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        file_name = f"InnoMedia_{project_id[:8]}.mp4"
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)
        
        # Ghi từng byte (chunk) của file video xuống ổ cứng
        with open(file_path, 'wb') as f:
            for chunk in resp_3.iter_content(chunk_size=8192):
                f.write(chunk)
                
        # --- BƯỚC 4: HOÀN TẤT 100% ---
        project.status = 'SUCCESS'
        project.final_video_path = f'/media/{file_name}'
        project.save()
        
        print(f"[Celery] 🎉 HOÀN TẤT THỰC SỰ! Video đã lưu tại: {file_path}\n")
        return {"status": "SUCCESS", "video_url": f'/media/{file_name}'}
        
    except requests.exceptions.RequestException as req_err:
        error_msg = f"Lỗi giao tiếp giữa các Service: {str(req_err)}"
        print(f"\n[Celery] ❌ {error_msg}\n")
        
        if project: 
            project.status = 'FAILED'
            project.error_message = error_msg
            project.save()
            
        # Loại bỏ self.update_state, Celery sẽ tự động cập nhật trạng thái FAILURE khi raise Exception
        raise Exception(error_msg)
        
    except Exception as e:
        error_msg = f"Lỗi hệ thống: {str(e)}"
        print(f"\n[Celery] ❌ LỖI: {error_msg}\n")
        
        if project: 
            project.status = 'FAILED'
            project.error_message = error_msg
            project.save()
            
        # Loại bỏ self.update_state, Celery sẽ tự động cập nhật trạng thái FAILURE khi raise Exception
        raise e

@shared_task(bind=True)
def re_render_video_pipeline(self, project_id: str):
    project = None
    try:
        project = VideoProject.objects.get(id=project_id)
        project.status = 'PROCESSING'
        project.save()
        
        # Bỏ qua Service 2, đi thẳng vào Service 3 với kịch bản đã có sẵn trong DB
        self.update_state(state='PROGRESS', meta={'percent': 30, 'message': 'Đang chuẩn bị kịch bản chỉnh sửa...'})
        print(f"[Celery Re-render] Đang gửi kịch bản mới tới Service 3...")
        
        script_data = project.script_data
        render_payload = build_video_plan_payload(script_data)
        
        self.update_state(state='PROGRESS', meta={'percent': 50, 'message': 'Xưởng phim đang dựng lại Video theo yêu cầu...'})
        
        # Gọi Service 3
        resp_3 = requests.post(SERVICE_3_URL, json=render_payload, timeout=600)
        resp_3.raise_for_status() 

        self.update_state(state='PROGRESS', meta={'percent': 90, 'message': 'Đang đóng gói Video mới...'})
        
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        # Thêm chữ _revised để phân biệt với bản gốc
        file_name = f"InnoMedia_{project_id[:8]}_revised.mp4"
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)
        
        with open(file_path, 'wb') as f:
            for chunk in resp_3.iter_content(chunk_size=8192):
                f.write(chunk)
                
        project.status = 'SUCCESS'
        project.final_video_path = f'/media/{file_name}'
        project.save()
        
        print(f"[Celery Re-render] 🎉 HOÀN TẤT DỰNG LẠI! Video mới: {file_path}\n")
        return {"status": "SUCCESS", "video_url": f'/media/{file_name}'}
        
    except Exception as e:
        error_msg = f"Lỗi hệ thống khi Re-render: {str(e)}"
        if project:
            project.status = 'FAILED'
            project.error_message = error_msg
            project.save()
            
        # Loại bỏ self.update_state, Celery sẽ tự động cập nhật trạng thái FAILURE khi raise Exception
        raise e
