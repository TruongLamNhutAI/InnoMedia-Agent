from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from graph import app as workflow_app

# ==========================================
# 1. KHỞI TẠO ỨNG DỤNG & METADATA
# ==========================================
app = FastAPI(
    title="InnoMedia-Agent: Agentic Orchestrator",
    description="Service 2: Core AI System quản lý vòng lặp tạo kịch bản và Visual Prompts",
    version="1.0.0"
)

# ==========================================
# 2. CẤU HÌNH BẢO MẬT (CORS MIDDLEWARE)
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Trên Production, sẽ thay "*" bằng IP của Service 1 (Django)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 3. ĐỊNH NGHĨA DATA SCHEMA CHO API
# ==========================================
class ScriptRequest(BaseModel):
    product_url: str

class ScriptResponse(BaseModel):
    status: str
    message: str
    data: list | None = None

# ==========================================
# 4. ĐỊNH NGHĨA CÁC ROUTES (API ENDPOINTS)
# ==========================================
@app.get("/health", tags=["System"])
async def health_check():
    """
    Endpoint sinh tồn: Dành cho Docker/Kubernetes ping vào 
    để kiểm tra xem container này có đang sống (healthy) hay bị treo.
    """
    return {"status": "ok", "service": "Agent_Orchestrator", "message": "Ready to accept tasks!"}

@app.post("/api/v1/generate-script", response_model=ScriptResponse, tags=["Agentic Flow"])
async def generate_script(request: ScriptRequest):
    """
    Endpoint chính để kích hoạt luồng LangGraph.
    Nhận URL từ Service 1, chạy qua Multi-Agent và trả về JSON cuối cùng.
    """
    try:
        print(f"\n[*] Đang nhận yêu cầu phân tích URL: {request.product_url}")
        
        # Khởi tạo Input State cho LangGraph
        initial_state = {
            "product_url": request.product_url,
            "retry_count": 0,
            "review_feedback": ""
        }
        
        # Dùng .invoke() thay vì .stream()
        # Vì đây là HTTP REST API, cần đợi graph chạy xong toàn bộ 
        # rồi mới gom kết quả cuối cùng (final_state) để trả về cho client.
        final_state = workflow_app.invoke(initial_state, config={"recursion_limit": 10})
        
        # Kiểm tra graph có xuất ra được kết quả như kỳ vọng 
        if "visual_prompts" in final_state and final_state["visual_prompts"]:
            print("[*] Luồng xử lý hoàn tất. Đang trả kết quả về cho Client.")
            return ScriptResponse(
                status="success",
                message="Kịch bản và Prompts đã được tạo thành công.",
                data=final_state["visual_prompts"]
            )
        else:
            # Graph bị ngắt giữa chừng do quá số lần retry hoặc lỗi ngầm
            raise HTTPException(status_code=400, detail="Hệ thống AI không thể sinh kịch bản đạt chuẩn. Vui lòng thử lại URL khác.")
            
    except Exception as e:
        print(f"[!] LỖI HỆ THỐNG: {str(e)}")
        # Trả về mã lỗi 500 kèm thông điệp để Gateway biết đường xử lý
        raise HTTPException(status_code=500, detail=f"Lỗi máy chủ AI: {str(e)}")

# ==========================================
# 5. KHỞI CHẠY SERVER LOCAL
# ==========================================
if __name__ == "__main__":
    # Reload=True giúp server tự động reset mỗi khi bấm Save code
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)