from pydantic import BaseModel
from typing import List, Optional

# --- OUTPUT MODELS (What the AI returns) ---
class Remedy(BaseModel):
    action: str
    details: str

class DiagnosisResult(BaseModel):
    plant_name: str
    status: str  # e.g., "Healthy", "Diseased"
    disease_name: Optional[str] = None
    confidence_score: float
    remedies: List[str]
    local_advice: str  # The "Kenyan context" advice
    sentinel_flag: bool = False # True if Sentinel flagged this as critical

# --- INPUT MODELS ---
class ChatRequest(BaseModel):
    question: str
    context: Optional[str] = None