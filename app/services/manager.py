from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.models.vertex_ai import VertexAIModel
from app.core import settings
from app.services import AgronomistService, SentinelService

class VunaGuideManager:
    def __init__(self):
        # Initialize Workers
        self.agronomist = AgronomistService()
        self.sentinel = SentinelService()
        
        self.model = VertexAIModel(
            model_name=settings.MODEL_ID,
            project_id=settings.GOOGLE_CLOUD_PROJECT,
            location=settings.LOCATION
        )

        # The Manager knows how to use the workers
        self.agent = Agent(
            name="VunaGuideManager",
            model=self.model,
            instruction="""
            You are the VunaGuide Orchestrator.
            1. Receive an image from the user.
            2. Call the 'diagnose_crop' tool to get the disease info.
            3. Call the 'audit_diagnosis' tool to check if that info is safe.
            4. If safe, return the diagnosis. If unsafe, add a warning.
            """,
            # ✅ HERE IS THE MAGIC: Agents as Tools!
            tools=[self.agronomist.diagnose_crop, self.sentinel.audit_diagnosis]
        )

    def process_request(self, image_bytes: bytes, mime_type: str):
        runner = Runner(agent=self.agent)
        
        # We need to manually guide the tool calls if using a pure LLM Manager,
        # OR we can just run the logic manually since we are the "Code Manager".
         
        # Step 1: Agronomist
        diagnosis = self.agronomist.diagnose_crop(image_bytes, mime_type)
        if not diagnosis:
            return {"error": "Diagnosis failed"}

        # Step 2: Sentinel
        audit = self.sentinel.audit_diagnosis(diagnosis)
        
        # Step 3: Merge
        if not audit.get("safe", True):
            diagnosis["sentinel_flag"] = True
            diagnosis["local_advice"] = f"⚠️ WARNING: {audit.get('reason')} " + diagnosis.get("local_advice", "")
            
        return diagnosis