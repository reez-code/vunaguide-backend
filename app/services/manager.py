import os
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.tools import google_search 
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.adk.models.google_llm import Gemini

from app.core import settings
from app.services import AgronomistService, SentinelService

class ManagerService:
    def __init__(self):
        self.agronomist = AgronomistService()
        self.sentinel = SentinelService()
        
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "1"
        os.environ["GOOGLE_CLOUD_PROJECT"] = settings.GOOGLE_CLOUD_PROJECT
        os.environ["GOOGLE_CLOUD_LOCATION"] = settings.LOCATION
        
        self.model = Gemini(model=settings.MODEL_ID)

        self.chat_agent = Agent(
            name="VunaGuideChat",
            model=self.model,
            instruction="""
            You are VunaGuide, a helpful Kenyan Agricultural Assistant.
            Answer questions about farming, seasons, and market prices.
            Use Google Search to get real-time information.
            Keep answers short and practical for farmers.
            """,
            tools=[google_search] 
        )

    async def process_request(self, image_bytes: bytes, mime_type: str, user_text: str = None) -> dict:
        # --- PATH A: CORE DIAGNOSIS ---
        if image_bytes:
            print("📸 Image detected. FORCING Diagnosis Pipeline.")
            
            diagnosis = await self.agronomist.diagnose_image(image_bytes, mime_type)
            
            if not diagnosis:
                return {"error": "Could not identify crop. Please try a clearer photo."}

            # ✅ FIX: Handle Non-Plant Images Gracefully
            if diagnosis.get("status") == "Not A Plant":
                print("🚫 Non-plant detected. Skipping Sentinel.")
                return diagnosis

            # Only run Sentinel if it IS a plant
            audit = await self.sentinel.audit_diagnosis(diagnosis)
            
            if not audit.get("safe", True):
                reason = audit.get("reason", "Unknown Safety Issue")
                diagnosis['local_advice'] = f"⚠️ SENTINEL WARNING: {reason}\n\n" + diagnosis.get("local_advice", "")
                diagnosis['sentinel_flag'] = True
            
            return diagnosis

        # --- PATH B: TEXT CHAT ---
        if user_text:
            print("💬 No image. Switching to Chat/Search Mode.")
            
            session_service = InMemorySessionService()
            runner = Runner(
                agent=self.chat_agent, 
                app_name="VunaGuide", 
                session_service=session_service
            )
            
            session = await session_service.create_session(app_name="VunaGuide", user_id="chat_user")
            
            user_message = types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_text)]
            )
            
            async for _ in runner.run_async(
                user_id="chat_user",
                session_id=session.id,
                new_message=user_message
            ):
                pass
            
            session = await session_service.get_session(app_name="VunaGuide", session_id=session.id, user_id="chat_user")
            final_text = ""
            
            if session.events:
                for event in reversed(session.events):
                    if event.content and event.content.parts:
                        has_text = False
                        for part in event.content.parts:
                            if part.text:
                                final_text = part.text
                                has_text = True
                        if has_text:
                            break

            return {
                "plant_name": "General Inquiry",
                "status": "Chat",
                "local_advice": final_text,
                "remedies": [],
                "confidence_score": 100
            }

        return {"error": "No input provided."}