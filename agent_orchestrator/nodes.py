import os
import json
from state import AgentState
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from typing import List
from schemas import (
    CritiqueResultSchema,
    InputDataSchema,
    MarketingStrategySchema,
    ProductDataSchema,
    PromptPlanItemSchema,
    QualityChecksSchema,
    ScenePlanItemSchema,
    ScriptDataSchema,
    VideoPlanSceneSchema,
    VideoPlanSchema,
)

class VideoScriptSchema(BaseModel): # Output Schema
    hook: str = Field(description="Câu mở đầu 3 giây, gây shock hoặc tò mò mạnh để giữ chân người xem.")
    body: str = Field(description="Phần nội dung chính, nêu bật tính năng và giải quyết nỗi đau của khách hàng.")
    cta: str = Field(description="Lời kêu gọi hành động (Call to Action) rõ ràng ở cuối video.")
    duration_estimate: int = Field(description="Ước tính thời lượng video (tính bằng giây).")

class ReviewResultSchema(BaseModel):
    is_approved: bool = Field(description="Quyết định phê duyệt: True (Duyệt) hoặc False (Từ chối).")
    feedback: str = Field(description="Lý do từ chối và hướng dẫn sửa chữa. Nếu duyệt, ghi 'Kịch bản tốt'.")

class ScenePrompt(BaseModel):
    scene_number: int = Field(description="Số thứ tự của phân cảnh (1, 2, 3...).")
    voiceover_text: str = Field(description="Lời thoại tiếng Việt sẽ được đọc (Voiceover/Subtitles) trong cảnh này. Trích xuất chính xác từ kịch bản gốc.")
    visual_prompt: str = Field(description="Câu lệnh prompt BẰNG TIẾNG ANH mô tả hình ảnh, góc máy, ánh sáng (không chứa chữ text).")
    duration: int = Field(description="Thời lượng cảnh (giây). Hãy tính toán logic: Tốc độ đọc tiếng Việt trung bình là 3-4 từ/giây. Đếm số từ trong voiceover_text để nội suy ra số giây, tối thiểu 3 giây.")

class VisualPromptListSchema(BaseModel):
    scenes: List[ScenePrompt] = Field(description="Danh sách các phân cảnh hoàn chỉnh để render video.")

# Load API Key từ file .env
load_dotenv()

# Khởi tạo mô hình AI 
# Ta dùng ChatGroq
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)

# Ép LLM phải trả về đúng cấu trúc Pydantic
structured_llm = llm.with_structured_output(VideoScriptSchema)

def write_script_node(state: AgentState):
    current_retry = state.get('retry_count', 0)
    print(f"\n[Node: Writer] Đang phân tích URL và viết kịch bản... (Lần thử: {current_retry + 1})")
    
    # 1. Viết System Prompt 
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Bạn là một Copywriter chuyên nghiệp trên TikTok/Reels cho các doanh nghiệp E-commerce.
        Nhiệm vụ của bạn là viết một kịch bản video ngắn (15-30s) siêu viral dựa trên đường link sản phẩm được cung cấp.
        
        YÊU CẦU BẮT BUỘC:
        - Giọng văn: Năng động, thu hút, đánh trúng tâm lý người mua.
        - Nếu có feedback từ Đạo diễn (Reviewer), BẮT BUỘC phải sửa kịch bản theo feedback đó."""),
        
        ("human", """
        Thông tin đầu vào:
        - Link/Tên sản phẩm: {product_url}
        - Lần viết lại thứ: {retry_count}
        - Feedback từ Đạo diễn (nếu có): {review_feedback}
        
        Hãy viết kịch bản ngay bây giờ.
        """)
    ])
    
    # 2. Tạo Chain (Nối Prompt -> LLM)
    chain = prompt | structured_llm
    
    # 3. Gọi LLM thực thi
    response = chain.invoke({
        "product_url": state.get("product_url"),
        "retry_count": current_retry,
        "review_feedback": state.get("review_feedback", "Không có. Đây là lần viết đầu tiên.")
    })
    
    # 4. Trả về State mới (response lúc này là 1 object đã được chuẩn hóa theo VideoScriptSchema)
    script_data = ScriptDataSchema(
        hook=response.hook,
        body=response.body,
        cta=response.cta,
        full_script=f"{response.hook}\n\n{response.body}\n\n{response.cta}",
        estimated_duration=response.duration_estimate,
        claims_used=[],
    )

    return {
        "raw_script": response.model_dump_json(), # Chuyển thành chuỗi JSON chuẩn để lưu
        "script_data": script_data.model_dump(),
        "retry_count": current_retry + 1
    }

# Ép AI Reviewer phải trả về đúng cấu trúc của ReviewResultSchema
reviewer_llm = llm.with_structured_output(ReviewResultSchema)

def review_script_node(state: AgentState):
    print("\n[Node: Reviewer] Đạo diễn AI đang chấm điểm kịch bản...")
    
    # 1. Lấy kịch bản từ state (Lưu ý: raw_script đang ở dạng JSON string)
    raw_script_json = state.get("raw_script")
    
    # 2. Viết System Prompt cho Đạo diễn 
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Bạn là một Giám đốc Marketing khó tính và thực dụng tại một Agency E-commerce hàng đầu.
        Nhiệm vụ của bạn là kiểm duyệt kịch bản video ngắn. Bạn CHỈ DUYỆT (is_approved = True) khi kịch bản thỏa mãn 100% các tiêu chí sau:
        
        1. HOOK (Mở đầu): Phải đánh trúng nỗi đau (pain point) hoặc gây tò mò cực mạnh trong 3 giây đầu. Tuyệt đối KHÔNG dùng những câu chào hỏi sáo rỗng kiểu "Chào các bạn".
        2. BODY: Có làm nổi bật được giá trị thiết thực của sản phẩm không?
        3. DURATION: Thời lượng không được lê thê, phải nhịp nhàng.
        
        Nếu kịch bản vi phạm dù chỉ 1 tiêu chí, hãy TỪ CHỐI (is_approved = False) và chỉ trích thẳng thắn, đưa ra hướng dẫn cụ thể để nhân viên Copywriter sửa lại."""),
        
        ("human", """
        Đây là kịch bản tôi vừa viết:
        {script_data}
        
        Hãy đưa ra quyết định đánh giá.
        """)
    ])
    
    # 3. Tạo Chain và gọi AI
    chain = prompt | reviewer_llm
    
    # Try-except để bắt lỗi trong trường hợp LLM gặp sự cố parse dữ liệu
    try:
        evaluation = chain.invoke({
            "script_data": raw_script_json
        })
        
        # 4. Trả về State mới dựa trên quyết định của Giám đốc AI
        if evaluation.is_approved:
            print("   -> ĐẠT: Kịch bản chốt sale xuất sắc! Cho phép đi tiếp.")
            critique = CritiqueResultSchema(
                approved=True,
                overall_score=8.0,
                hook_score=8.0,
                clarity_score=8.0,
                conversion_score=8.0,
                platform_fit_score=8.0,
                issues=[],
                revision_instruction="",
            )
            return {
                "script_approved": True,
                "critique": critique.model_dump(),
                "review_feedback": "" # Xóa feedback cũ vì đã đạt
            }
        else:
            print(f"   -> TỪ CHỐI: {evaluation.feedback}")
            critique = CritiqueResultSchema(
                approved=False,
                overall_score=5.0,
                hook_score=5.0,
                clarity_score=5.0,
                conversion_score=5.0,
                platform_fit_score=5.0,
                issues=[evaluation.feedback],
                revision_instruction=evaluation.feedback,
            )
            return {
                "script_approved": False,
                "critique": critique.model_dump(),
                "review_feedback": evaluation.feedback # Gửi feedback này ngược lại cho Writer
            }
            
    except Exception as e:
        print(f"   -> [LỖI HỆ THỐNG REVIEW]: {str(e)}")
        # Đề phòng lỗi API, bắt luồng quay lại hoặc ngắt tùy thiết kế
        return {
            "script_approved": False,
            "review_feedback": "Lỗi hệ thống khi đánh giá, vui lòng sinh lại kịch bản."
        }

# Khởi tạo bộ parse cho Prompter
visual_llm = llm.with_structured_output(VisualPromptListSchema)

def visual_prompt_node(state: AgentState):
    print("\n[Node: Prompter] Đang bóc tách Lời thoại và chuyển đổi Visual Prompts...")
    
    raw_script_json = state.get("raw_script")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Bạn là một Đạo diễn kỹ thuật (Technical Director) xuất sắc.
        Nhiệm vụ của bạn là lấy kịch bản video tiếng Việt đã được duyệt và "băm" (breakdown) nó thành một bảng phân cảnh chi tiết (Storyboard) để giao cho đội Media Engine.
        
        QUY TRÌNH THỰC HIỆN:
        1. CHIA CẢNH: Chia kịch bản thành các phân cảnh hợp lý.
        2. LỜI THOẠI (voiceover_text): Trích xuất chính xác từng câu nói tiếng Việt trong kịch bản gán vào từng cảnh.
        3. HÌNH ẢNH (visual_prompt): Tưởng tượng hình ảnh minh họa cho câu thoại đó và viết lệnh prompt BẰNG TIẾNG ANH.
           - Công thức: [Main Subject] + [Action] + [Setting/Background] + [Camera Movement] + [Lighting: cinematic, 4k].
        4. THỜI LƯỢNG (duration): Tự động tính số giây cần thiết để đọc hết câu thoại đó (trung bình 1 giây đọc được 3-4 từ).
        
        TUYỆT ĐỐI không thêm các ký tự Markdown hay giải thích thừa. Chỉ trả về JSON hợp lệ."""),
        
        ("human", """
        Kịch bản đầu vào:
        {script_data}
        """)
    ])
    
    chain = prompt | visual_llm
    
    try:
        result = chain.invoke({"script_data": raw_script_json})
        prompts_data = [scene.model_dump() for scene in result.scenes]
        scene_plan = {
            "scenes": [
                ScenePlanItemSchema(
                    scene_number=scene["scene_number"],
                    duration=scene["duration"],
                    voiceover_text=scene["voiceover_text"],
                    subtitle_text=scene["voiceover_text"],
                    scene_goal="conversion_step",
                    visual_description=scene["visual_prompt"],
                    product_focus=True,
                    transition="cut",
                ).model_dump()
                for scene in prompts_data
            ]
        }
        prompt_plan = {
            "scenes": [
                PromptPlanItemSchema(
                    scene_number=scene["scene_number"],
                    image_prompt=scene["visual_prompt"],
                    consistency_notes="Keep the same product identity and visual style across scenes.",
                ).model_dump()
                for scene in prompts_data
            ]
        }
        
        print(f"   -> THÀNH CÔNG: Đã xuất bản {len(prompts_data)} phân cảnh hoàn chỉnh (Có Voiceover + Prompt)!")
        return {
            "visual_prompts": prompts_data,
            "scene_plan": scene_plan,
            "prompt_plan": prompt_plan,
        }
        
    except Exception as e:
        print(f"   -> [LỖI HỆ THỐNG PROMPTER]: {str(e)}")
        return {"visual_prompts": [], "errors": [str(e)]}


def finalize_video_plan_node(state: AgentState):
    print("\n[Node: Finalizer] Đang đóng gói Video Plan chuẩn cho Media Engine...")

    product_url = state.get("product_url", "")
    input_data = InputDataSchema(product_url=product_url)
    product_data = ProductDataSchema(
        name=product_url,
        description=product_url,
        selling_points=[],
        pain_points=[],
        risk_notes=["Phase 1 placeholder: Product Agent/RAG chưa được kích hoạt."],
    )
    marketing_strategy = MarketingStrategySchema(
        selected_hooks=[state.get("script_data", {}).get("hook", "")],
        selected_ctas=[state.get("script_data", {}).get("cta", "")],
    )
    script_data = state.get("script_data") or {}
    critique = state.get("critique") or {}
    visual_prompts = state.get("visual_prompts") or []

    scenes = []
    for scene in visual_prompts:
        voiceover_text = scene.get("voiceover_text", "")
        image_prompt = scene.get("visual_prompt", "")
        scenes.append(
            VideoPlanSceneSchema(
                scene_number=scene.get("scene_number", len(scenes) + 1),
                duration=scene.get("duration", 3),
                voiceover_text=voiceover_text,
                subtitle_text=voiceover_text,
                scene_goal="conversion_step",
                visual_description=image_prompt,
                product_focus=True,
                transition="cut",
                image_prompt=image_prompt,
                visual_prompt=image_prompt,
                visual_style=marketing_strategy.visual_style,
            )
        )

    video_plan = VideoPlanSchema(
        platform=input_data.platform,
        aspect_ratio="9:16",
        duration=script_data.get("estimated_duration", input_data.video_duration),
        language=input_data.language,
        video_goal=marketing_strategy.video_goal,
        product=product_data,
        marketing_strategy=marketing_strategy,
        script=ScriptDataSchema(**script_data),
        scenes=scenes,
        quality_checks=QualityChecksSchema(
            script_score=critique.get("overall_score", 0),
            visual_consistency_score=8.0 if scenes else 0,
        ),
        metadata={
            "contract_version": "video_plan.v1",
            "phase": "phase_1_schema_standardization",
            "input_data": input_data.model_dump(),
        },
    )

    print(f"   -> Video Plan đã sẵn sàng với {len(scenes)} cảnh.")
    return {
        "input_data": input_data.model_dump(),
        "product_data": product_data.model_dump(),
        "marketing_strategy": marketing_strategy.model_dump(),
        "video_plan": video_plan.model_dump(),
    }
