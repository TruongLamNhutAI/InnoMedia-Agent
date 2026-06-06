from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class InputDataSchema(BaseModel):
    product_url: str = Field(description="Link, ten san pham, hoac mo ta san pham dau vao.")
    product_images: List[str] = Field(default_factory=list)
    custom_images: List[str] = Field(default_factory=list)
    product_description: str = ""
    target_audience: str = "general"
    platform: str = "tiktok"
    video_duration: int = 30
    video_style: str = "review"
    language: str = "vi"
    tone: str = "energetic"
    extra_instruction: str = ""


class ProductDataSchema(BaseModel):
    name: str = ""
    category: str = "unknown"
    brand: str = ""
    price: str = ""
    description: str = ""
    selling_points: List[str] = Field(default_factory=list)
    pain_points: List[str] = Field(default_factory=list)
    reviews_summary: List[str] = Field(default_factory=list)
    risk_notes: List[str] = Field(default_factory=list)


class MarketingStrategySchema(BaseModel):
    video_goal: str = "conversion"
    hook_strategy: str = "pain_point"
    story_structure: str = "hook -> problem -> benefit -> CTA"
    selected_hooks: List[str] = Field(default_factory=list)
    selected_ctas: List[str] = Field(default_factory=list)
    visual_style: str = "cinematic product demo"
    persuasion_angle: str = "highlight practical benefits"
    avoid: List[str] = Field(default_factory=list)


class ScriptDataSchema(BaseModel):
    hook: str
    body: str
    cta: str
    full_script: str
    estimated_duration: int
    claims_used: List[str] = Field(default_factory=list)


class CritiqueResultSchema(BaseModel):
    approved: bool
    overall_score: float = 0
    hook_score: float = 0
    clarity_score: float = 0
    conversion_score: float = 0
    platform_fit_score: float = 0
    issues: List[str] = Field(default_factory=list)
    revision_instruction: str = ""


class ScenePlanItemSchema(BaseModel):
    scene_number: int
    duration: int
    voiceover_text: str
    subtitle_text: str
    scene_goal: str = ""
    visual_description: str = ""
    product_focus: bool = True
    transition: str = "cut"


class PromptPlanItemSchema(BaseModel):
    scene_number: int
    image_prompt: str
    negative_prompt: str = "text, watermark, logo, distorted product, low quality"
    camera: str = "vertical product ad framing"
    lighting: str = "cinematic soft lighting"
    style_tags: List[str] = Field(default_factory=lambda: ["vertical video", "9:16", "commercial"])
    consistency_notes: str = ""


class VideoPlanSceneSchema(ScenePlanItemSchema):
    image_prompt: str
    visual_prompt: str
    negative_prompt: str = "text, watermark, logo, distorted product, low quality"
    visual_style: str = "cinematic product demo"
    camera: str = "vertical product ad framing"


class MusicPlanSchema(BaseModel):
    style: str = "lofi"
    volume: float = 0.3


class QualityChecksSchema(BaseModel):
    script_score: float = 0
    visual_consistency_score: float = 0


class VideoPlanSchema(BaseModel):
    project_id: Optional[str] = None
    platform: str = "tiktok"
    aspect_ratio: str = "9:16"
    duration: int = 30
    language: str = "vi"
    video_goal: str = "conversion"
    product: ProductDataSchema = Field(default_factory=ProductDataSchema)
    marketing_strategy: MarketingStrategySchema = Field(default_factory=MarketingStrategySchema)
    script: ScriptDataSchema
    scenes: List[VideoPlanSceneSchema]
    music: MusicPlanSchema = Field(default_factory=MusicPlanSchema)
    quality_checks: QualityChecksSchema = Field(default_factory=QualityChecksSchema)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentResponseSchema(BaseModel):
    status: str
    message: str
    video_plan: VideoPlanSchema
    data: List[VideoPlanSceneSchema]
