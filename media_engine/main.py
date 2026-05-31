import os
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
from generators.tts_generator import generate_audio_from_text
from generators.video_generator import generate_visual_from_prompt
from processors.video_editor import assemble_video

app = FastAPI(
    title="InnoMedia-Agent: Media Engine",
    description="Service 3: Xưởng render Video, Audio và Subtitles tự động",
    version="1.0.0"
)

# --- 1. ĐỊNH NGHĨA SCHEMA ĐẦU VÀO TỪ SERVICE 2 ---
class SceneSchema(BaseModel):
    scene_number: int
    voiceover_text: str
    visual_prompt: str
    duration: int

class RenderRequest(BaseModel):
    scenes: List[SceneSchema]

# --- 2. API ENDPOINT ĐỂ DJANGO GỌI VÀO (CHẠY TUẦN TỰ TỐI ƯU) ---
@app.post("/api/v1/render", tags=["Media Factory"])
async def render_video_endpoint(request: RenderRequest):
    print("\n[*] NHẬN LỆNH RENDER TỪ SERVICE 1 (DJANGO)...")
    try:
        scene_assets = []
        
        # ÉP CHẠY TUẦN TỰ TỪNG CẢNH MỘT (CHỐNG SPAM API TUYỆT ĐỐI)
        for index, scene in enumerate(request.scenes, start=1):
            print(f"\n--- ĐANG TẢI TÀI NGUYÊN PHÂN CẢNH {index}/{len(request.scenes)} ---")
            text = scene.voiceover_text
            prompt = scene.visual_prompt
            
            # 1. Sinh ảnh và BẮT BUỘC CHỜ kết quả
            img_path = await generate_visual_from_prompt(prompt, index)
            await asyncio.sleep(2) # Trạm nghỉ 2 giây làm dịu server
            
            # 2. Sinh âm thanh và BẮT BUỘC CHỜ kết quả
            aud_path = await generate_audio_from_text(text, index)
            await asyncio.sleep(2) # Trạm nghỉ 2 giây trước khi sang cảnh tiếp theo
            
            scene_assets.append({
                "image_path": img_path,
                "audio_path": aud_path,
                "voiceover_text": text
            })
            
        # Phase 2: Dựng Video
        output_name = f"InnoMedia_Output_{os.urandom(4).hex()}.mp4"
        
        # Gọi hàm assemble_video để dựng video từ các assets đã tạo (ảnh + âm thanh)
        final_mp4 = assemble_video(scene_assets, output_filename=output_name)
        
        if final_mp4 and os.path.exists(final_mp4):
            print(f"[*] RENDER THÀNH CÔNG. Đang gửi trả file cho Client...")
            # Trả thẳng file MP4 về cho client (Django) tải xuống!
            return FileResponse(final_mp4, media_type="video/mp4", filename=output_name)
        else:
            raise HTTPException(status_code=500, detail="Lỗi trong quá trình Render Video (Phase 2).")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "service": "Media_Engine"}

if __name__ == "__main__":
    import uvicorn
    # Mở cổng 8001 để không trùng cổng 8000 của Service 2
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)