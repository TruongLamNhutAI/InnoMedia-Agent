
from typing import TypedDict, List, Any, Optional

class AgentState(TypedDict):
    product_url: str
    raw_script: str
    script_approved: bool
    review_feedback: str
    visual_prompts: List[Any] # Hoặc List[dict] để nhận dữ liệu từ Prompter
    retry_count: int