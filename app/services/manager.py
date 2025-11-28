from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.models.vertex_ai import VertexAIModel
from google.genai import types
from app.core import settings
from app.services import AgronomistService, SentinelService

# Native Google Search Tool (Only for text questions)
google_search_tool = types.Tool(
    google_search_retrieval=types.GoogleSearchRetrieval()
)

class ManagerService:
    def __init__(self):
        # The Core Workers
        self.agronomist = AgronomistService()
        self.sentinel = SentinelService()
        
        self.model = VertexAIModel(
            model_name=settings.MODEL_ID,
            project_id=settings.GOOGLE_CLOUD_PROJECT,
            location=settings.LOCATION
        )

        # The Chat Agent (Only used if NO image is uploaded)
        self.chat_agent = Agent(
            name="VunaGuideChat",
            model=self.model,
            instruction="""
            You are VunaGuide, a helpful Kenyan Agricultural Assistant.
            Answer questions about farming, seasons, and market prices.
            Use Google Search to get real-time information.
            Keep answers short and practical for farmers.
            """,
            tools=[google_search_tool]
        )

    def process_request(self, image_bytes: bytes, mime_type: str, user_text: str = None) -> dict:
        """
        STRICT LOGIC FLOW:
        1. Image Uploaded? -> RUN DIAGNOSIS PIPELINE (Core Feature).
        2. No Image? -> RUN CHAT AGENT (Support Feature).
        """
        
        # --- PATH A: CORE DIAGNOSIS (High Priority) ---
        if image_bytes:
            print("📸 Image detected. FORCING Diagnosis Pipeline.")
            
            # 1. Run Agronomist (Vision)
            diagnosis = self.agronomist.diagnose_image(image_bytes, mime_type)
            
            if not diagnosis:
                return {"error": "Could not identify crop."}

            # 2. Run Sentinel (Safety)
            audit = self.sentinel.audit_diagnosis(diagnosis)
            
            # 3. Merge Results
            if not audit.get("safe", True):
                reason = audit.get("reason", "Unknown Safety Issue")
                diagnosis['local_advice'] = f"⚠️ SENTINEL WARNING: {reason}\n\n" + diagnosis.get("local_advice", "")
                diagnosis['sentinel_flag'] = True
            
            return diagnosis

        # --- PATH B: TEXT CHAT (Low Priority / Support) ---
        if user_text:
            print("💬 No image. Switching to Chat/Search Mode.")
            runner = Runner(agent=self.chat_agent)
            result = runner.run(user_text)
            
            return {
                "plant_name": "General Inquiry",
                "status": "Chat",
                "local_advice": result.text, # Contains Google Search answer
                "remedies": [],
                "confidence_score": 100
            }

        return {"error": "No input provided."}