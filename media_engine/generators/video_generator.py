import os
import requests
import asyncio
import urllib.parse
import uuid
import time 

WORKSPACE_DIR = os.path.join(os.getcwd(), "workspace")
os.makedirs(WORKSPACE_DIR, exist_ok=True)

async def generate_visual_from_prompt(prompt: str, scene_number: int) -> str:
    """
    Nhận Visual Prompt tiếng Anh và gọi API miễn phí để sinh ảnh 1080x1920.
    Trả về đường dẫn tuyệt đối của file JPG.
    """
    print(f"[Visual Engine] Đang tạo hình ảnh (Tỉ lệ 9:16) cho Phân cảnh {scene_number}...")
    
    # Mã hóa chuỗi prompt để đưa vào URL an toàn
    encoded_prompt = urllib.parse.quote(prompt)
    
    # Sử dụng API miễn phí của Pollinations (Tạo ảnh dọc chuẩn Reels/TikTok)
    # Tham số nologo=true để xóa watermark
    api_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&nologo=true"
    
    file_name = f"scene_{scene_number}_{uuid.uuid4().hex[:8]}.jpg"
    file_path = os.path.join(WORKSPACE_DIR, file_name)
    
    # Hàm chạy đồng bộ bọc trong luồng phụ, CÓ CƠ CHẾ RETRY
    def fetch_image():
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Tăng timeout lên 25s vì sinh ảnh đôi khi server queue khá lâu
                response = requests.get(api_url, timeout=25) 
                if response.status_code == 200:
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    return file_path
                else:
                    print(f"   -> [CẢNH BÁO] Thử lần {attempt + 1}: Server API lỗi {response.status_code}")
            except Exception as e:
                print(f"   -> [CẢNH BÁO] Thử lần {attempt + 1}: Mạng chậm hoặc Timeout.")
            
            # Nếu chưa phải lần thử cuối cùng thì nghỉ 2 giây rồi gọi lại
            if attempt < max_retries - 1:
                # Tính toán thời gian nghỉ giãn cách (2s -> 4s -> 8s)
                wait_time = 2 ** (attempt + 1) 
                print(f"   -> Đang làm dịu server, chờ {wait_time}s trước khi thử lại...")
                time.sleep(wait_time)
                
        # Sau 3 lần vẫn trượt thì mới chịu thua
        print(f"   -> [LỖI VISUAL API]: Đầu hàng sau {max_retries} lần thử cho Cảnh {scene_number}.")
        return ""

    # Chạy bất đồng bộ
    result_path = await asyncio.to_thread(fetch_image)
    
    if result_path:
        print(f"   -> [THÀNH CÔNG] Đã lưu hình ảnh: {result_path}")
    else:
        print(f"   -> [THẤT BẠI] Không thể tạo ảnh cho cảnh {scene_number}")
        
    return result_path