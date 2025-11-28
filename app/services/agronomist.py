import json
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.models.vertex_ai import VertexAIModel
from google.genai import types
from app.core import settings
from app.tools import submit_diagnosis_report # Your submission tool structure

class AgronomistService:
    def __init__(self):
        self.model = VertexAIModel(
            model_name=settings.MODEL_ID,
            project_id=settings.GOOGLE_CLOUD_PROJECT,
            location=settings.LOCATION
        )

        self.agent = Agent(
            name="AgronomistWorker",
            model=self.model,
            instruction="""
            Analyze the crop image.
            Identify disease, confidence, and remedies.
            Use 'submit_diagnosis_report' to structure your findings.
            """,
            tools=[submit_diagnosis_report]
        )

    # This is the "Tool" function for the Root Agent
    def diagnose_crop(self, image_bytes: bytes, mime_type: str) -> dict:
        """
        Performs visual diagnosis on a crop image.
        """
        runner = Runner(agent=self.agent)
        
        user_input = [
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            "Analyze this crop and submit the report."
        ]
        
        try:
            print("🌿 Agronomist Agent running...")
            result = runner.run(user_input)
            
            # Extract tool output from history
            for turn in result.turns:
                for part in turn.parts:
                    if hasattr(part, "function_call") and part.function_call:
                        if part.function_call.name == "submit_diagnosis_report":
                            return dict(part.function_call.args)
            return None
        except Exception as e:
            print(f"❌ Agronomist Error: {e}")
            raise e