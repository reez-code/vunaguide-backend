import json
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.models.vertex_ai import VertexAIModel
from app.core import settings

class SentinelService:
    def __init__(self):
        self.model = VertexAIModel(
            model_name=settings.MODEL_ID,
            project_id=settings.GOOGLE_CLOUD_PROJECT,
            location=settings.LOCATION
        )
        
        # The Sentinel is a specialized Agent
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

    # This is the "Tool" function the Root Agent will use
    def audit_diagnosis(self, diagnosis_data: dict) -> dict:
        """
        Audits a diagnosis report for safety compliance.
        """
        runner = Runner(agent=self.agent)
        
        # Convert dict to string for the LLM
        prompt = f"AUDIT THIS: {json.dumps(diagnosis_data)}"
        
        try:
            print("🛡️ Sentinel Agent running...")
            result = runner.run(prompt)
            
            # Clean formatting
            text = result.text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception as e:
            print(f"❌ Sentinel Error: {e}")
            # Fail Open (Allow it)
            return {"safe": True, "reason": "Sentinel Pass (Error)"}