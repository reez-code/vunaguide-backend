import os
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.adk.models.google_llm import Gemini
from app.core import settings
from app.tools import submit_diagnosis_report

class AgronomistService:
    def __init__(self):
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "1"
        os.environ["GOOGLE_CLOUD_PROJECT"] = settings.GOOGLE_CLOUD_PROJECT
        os.environ["GOOGLE_CLOUD_LOCATION"] = settings.LOCATION
        
        self.model = Gemini(model=settings.MODEL_ID)

        self.agent = Agent(
            name="AgronomistWorker",
            model=self.model,
            instruction="""
            You are VunaGuide, an expert Agronomist.
            Analyze the image provided.
            
            SCENARIO 1: IT IS A CROP/PLANT
            - Identify plant, disease, and remedies.
            - Call 'submit_diagnosis_report' with status='Diseased' or 'Healthy'.
            - For 'local_advice', provide practical advice in clear English suitable for farmers.
            
            SCENARIO 2: IT IS NOT A PLANT (e.g. Animal, Person, Car, Object)
            - Call 'submit_diagnosis_report' IMMEDIATELY.
            - Set status='Not A Plant'.
            - Set plant_name='Unknown'.
            - Set local_advice='Sorry, I only analyze crops. Please upload a photo of a plant.'
            - Set remedies=[] and confidence_score=0.
            
            YOU MUST CALL THE TOOL IN BOTH SCENARIOS.
            """,
            tools=[submit_diagnosis_report]
        )

    async def diagnose_image(self, image_bytes: bytes, mime_type: str) -> dict:
        session_service = InMemorySessionService()
        runner = Runner(
            agent=self.agent, 
            app_name="VunaGuide", 
            session_service=session_service
        )
        
        session = await session_service.create_session(app_name="VunaGuide", user_id="agro_worker")
        
        print("🌿 Agronomist Agent running...")
        
        try:
            user_input = types.Content(
                role="user",
                parts=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    types.Part.from_text(text="Analyze this image.")
                ]
            )

            async for _ in runner.run_async(
                user_id="agro_worker",
                session_id=session.id,
                new_message=user_input
            ):
                pass

            session = await session_service.get_session(
                app_name="VunaGuide", 
                session_id=session.id, 
                user_id="agro_worker"
            )
            
            if session.events:
                for event in session.events:
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if part.function_call and part.function_call.name == "submit_diagnosis_report":
                                print("✅ Agronomist Tool Call Detected")
                                return dict(part.function_call.args)
            
            print("⚠️ Agronomist failed to call tool.")
            return None
            
        except Exception as e:
            print(f"❌ Agronomist Error: {e}")
            raise e