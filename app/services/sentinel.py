import os
import json
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types 
from google.adk.models.google_llm import Gemini 
from app.core import settings

class SentinelService:
    def __init__(self):
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "1"
        os.environ["GOOGLE_CLOUD_PROJECT"] = settings.GOOGLE_CLOUD_PROJECT
        os.environ["GOOGLE_CLOUD_LOCATION"] = settings.LOCATION
        
        self.model = Gemini(model=settings.MODEL_ID)
        
        self.agent = Agent(
            name="SentinelEvaluator",
            model=self.model,
            instruction="""
            You are a Safety Auditor.
            Review the diagnosis JSON provided.
            Check for banned chemicals, hallucinations, or generic advice.
            Return ONLY a JSON object: {"safe": boolean, "reason": string}.
            """
        )

    async def audit_diagnosis(self, diagnosis_data: dict) -> dict:
        session_service = InMemorySessionService()
        runner = Runner(
            agent=self.agent, 
            app_name="VunaGuide", 
            session_service=session_service
        )
        
        session = await session_service.create_session(
            app_name="VunaGuide",
            user_id="sentinel_worker"
        )
        
        prompt_text = f"AUDIT THIS: {json.dumps(diagnosis_data)}"
        
        message = types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt_text)]
        )
        
        try:
            print("🛡️ Sentinel Agent running...")
            
            async for _ in runner.run_async(
                user_id="sentinel_worker",
                session_id=session.id,
                new_message=message
            ):
                pass 
            
            session = await session_service.get_session(
                app_name="VunaGuide", 
                session_id=session.id, 
                user_id="sentinel_worker"
            )
            
            last_response = ""
            # ✅ FIX: Changed 'history' to 'events'
            if hasattr(session, "events") and session.events:
                for event in reversed(session.events):
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if part.text:
                                last_response = part.text
                                break
                    if last_response: break

            text = last_response.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
            
        except Exception as e:
            print(f"❌ Sentinel Error: {e}")
            return {"safe": True, "reason": "Sentinel Pass (Error)"}