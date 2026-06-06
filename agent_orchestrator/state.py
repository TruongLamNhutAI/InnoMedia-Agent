
from typing import Any, Dict, List, TypedDict

class AgentState(TypedDict, total=False):
    product_url: str
    input_data: Dict[str, Any]
    product_data: Dict[str, Any]
    marketing_strategy: Dict[str, Any]
    raw_script: str
    script_data: Dict[str, Any]
    script_approved: bool
    critique: Dict[str, Any]
    review_feedback: str
    visual_prompts: List[Any] # Hoặc List[dict] để nhận dữ liệu từ Prompter
    scene_plan: Dict[str, Any]
    prompt_plan: Dict[str, Any]
    video_plan: Dict[str, Any]
    retry_count: int
    errors: List[str]
