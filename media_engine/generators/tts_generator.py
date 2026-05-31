import os
import edge_tts
import uuid
import asyncio

# Đảm bảo thư mục workspace tồn tại
WORKSPACE_DIR = os.path.join(os.getcwd(), "workspace")
os.makedirs(WORKSPACE_DIR, exist_ok=True)

async def generate_audio_from_text(text: str, scene_number: int) -> str:
    """
    Nhận vào text tiếng Việt và sinh ra file MP3.
    """
    print(f"[TTS Engine] Đang sinh âm thanh cho Phân cảnh {scene_number}...")
    
    # Giọng nữ tiếng Việt (HoaiMyNeural)
    voice = "vi-VN-HoaiMyNeural" 
    file_name = f"scene_{scene_number}_{uuid.uuid4().hex[:8]}.mp3"
    file_path = os.path.join(WORKSPACE_DIR, file_name)
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(file_path)
            
            # Kiểm tra xem file có thực sự được lưu không
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                print(f"   -> [THÀNH CÔNG] Đã lưu file: {file_path}")
                return file_path
            else:
                 print(f"   -> [CẢNH BÁO] Lần {attempt+1}: File audio bị rỗng.")
                 
        except Exception as e:
            print(f"   -> [LỖI TTS] Lần {attempt+1}: {str(e)}")
            
        if attempt < max_retries - 1:
                # Tính toán thời gian nghỉ giãn cách (2s -> 4s -> 8s)
                wait_time = 2 ** (attempt + 1) 
                print(f"   -> Đang làm dịu server, chờ {wait_time}s trước khi thử lại...")
                await asyncio.sleep(wait_time)
             
    print(f"   -> [THẤT BẠI] Đầu hàng sau {max_retries} lần thử TTS cho cảnh {scene_number}.")
    return ""