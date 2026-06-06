import os
import subprocess
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
from imageio_ffmpeg import get_ffmpeg_exe
from moviepy.config import change_settings 

# --- CÁC CẤU HÌNH BẮT BUỘC ---
os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/convert"
change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"}) 

import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

WORKSPACE_DIR = os.path.join(os.getcwd(), "workspace")
BGM_PATH = os.path.join(os.getcwd(), "assets", "bgm_lofi.mp3")
FONT_PATH = os.path.join(os.getcwd(), "assets", "BeVietnamPro-ExtraBold.ttf")

def assemble_video(scene_assets: list, output_filename="final_commercial.mp4") -> str:
    print("\n[Video Editor] Đưa các nguyên liệu vào bàn dựng (INDUSTRY STANDARD MODE)...")
    
    video_clips = []
    
    try:
        for index, asset in enumerate(scene_assets):
            img_path = asset.get("image_path")
            aud_path = asset.get("audio_path")
            text = asset.get("voiceover_text", "")
            
            if not img_path or not aud_path or not os.path.exists(img_path) or not os.path.exists(aud_path):
                continue
                
            audio_clip = AudioFileClip(aud_path)
            actual_duration = audio_clip.duration
            
            image_clip = ImageClip(img_path).set_duration(actual_duration).resize(width=1080, height=1920)
            
            subtitle_clip = TextClip(
                text,           # Ép toàn bộ chữ thành .upper() để tăng độ nổi bật
                fontsize=60,            # Tăng size chữ để nổi bật trên nền ảnh
                color='white',          # Mã màu 
                font=FONT_PATH,         # Trỏ tới font siêu đậm (Black/ExtraBold)
                stroke_color='black',   # Thêm viền màu đen
                stroke_width=3,         # Độ dày của viền đen 
                method='caption',       
                # align='center',
                size=(900, None)        # Giới hạn chiều rộng để text tự xuống dòng
            ).set_position(('center', 1500)).set_duration(actual_duration)
            
            composite_scene = CompositeVideoClip([image_clip, subtitle_clip])
            final_scene = composite_scene.set_audio(audio_clip)
            
            video_clips.append(final_scene)
            print(f"   -> Đã xử lý Cảnh {index + 1}: Thêm Phụ đề & Sync Audio ({actual_duration:.1f}s)")
            
        if not video_clips:
            raise Exception("Không có phân cảnh hợp lệ")
            
        # 1. Dùng MoviePy ghép Hình + Phụ đề + Voiceover (Chưa có BGM)
        print("[Video Editor] Đang nối các phân cảnh...")
        final_video = concatenate_videoclips(video_clips, method="compose")
        
        temp_video_path = os.path.join(WORKSPACE_DIR, "temp_no_bgm.mp4")
        output_path = os.path.join(WORKSPACE_DIR, output_filename)
        
        print("[Video Editor] Bước 1: Render file MP4 (Hình + Voiceover)...")
        final_video.write_videofile(
            temp_video_path, 
            fps=24, 
            codec="libx264", 
            audio_codec="libmp3lame", 
            remove_temp=True,
            logger=None 
        )
        
        # 2. Dùng FFMPEG CLI để mix BGM
        if os.path.exists(BGM_PATH):
            print("[Video Editor] Bước 2: Mix Nhạc nền bằng FFMPEG Lõi (Siêu Tốc)...")
            ffmpeg_exe = get_ffmpeg_exe()
            
            # Khai báo câu lệnh FFMPEG: Mix 2 luồng audio, giảm volume BGM xuống 0.8, KHÔNG render lại video (-c:v copy)
            ffmpeg_cmd = [
                ffmpeg_exe, "-y",
                "-i", temp_video_path,
                "-i", BGM_PATH,
                "-filter_complex", "[1:a]volume=0.8[bgm];[0:a][bgm]amix=inputs=2:duration=first[a]",
                "-map", "0:v",
                "-map", "[a]",
                "-c:v", "copy", 
                "-c:a", "aac",
                output_path
            ]
            
            # Thực thi tiến trình FFMPEG ở cấp độ Hệ điều hành
            subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Xóa rác
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)
                
        else:
            print("[CẢNH BÁO] Không có bgm_lofi.mp3. Bỏ qua mix nhạc.")
            os.rename(temp_video_path, output_path)

        print(f"\n[XUẤT XƯỞNG] Video Đỉnh Cao đã hoàn thành tại: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"[LỖI RENDER VIDEO]: {str(e)}")
        raise