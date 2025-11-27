from google.adk.agents import LlmAgent  # <--- FIXED: Use LlmAgent
from google.adk.runners import Runner
from google.adk.models.vertex_ai import VertexAIModel
from app.core import settings
from app.tools import submit_diagnosis_report

class AgronomistService:
    def __init__(self):
        # 1. Define the Model
        self.model = VertexAIModel(
            model_name=settings.MODEL_ID,
            project_id=settings.GOOGLE_CLOUD_PROJECT,
            location=settings.LOCATION
        )

        # 2. Define the Agent (Persona)
        # We use LlmAgent which is optimized for GenAI workflows
        self.agent = LlmAgent(
            name="VunaGuideAgronomist",
            model=self.model,
            instruction="""
            You are VunaGuide, an expert Kenyan Agronomist.
            Your ONLY goal is to analyze the crop and SUBMIT a report using the tool.
            1. Identify the plant and disease.
            2. Suggest Kenyan remedies (e.g. Ridomil, Duduthrin).
            3. Use the 'submit_diagnosis_report' tool to finalize the result.
            """,
            tools=[submit_diagnosis_report]
        )

    def diagnose_image(self, image_bytes: bytes, mime_type: str) -> dict:
        # 3. Create a Runner (Orchestrator)
        runner = Runner(agent=self.agent)

        print("🤖 ADK Agent Running...")
        
        try:
            # Construct Multimodal Input
            # Note: Ensure you import 'types' from the standard google-genai SDK
            from google.genai import types
            user_input = [
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                "Analyze this crop and submit the report."
            ]

            # 4. EXECUTE & USE THE RESULT (The Fix)
            result = runner.run(user_input)
            
            # Now we actually USE 'result' to find the tool output
            # 'result.turns' contains the conversation steps from this run
            for turn in result.turns:
                for part in turn.parts:
                    # Check if this part is a Function Call
                    if hasattr(part, "function_call") and part.function_call:
                        if part.function_call.name == "submit_diagnosis_report":
                            print(f"✅ Tool Call Found: {part.function_call.name}")
                            
                            # Extract arguments
                            tool_args = dict(part.function_call.args)
                            
                            # Helper: Map 'is_severe' to 'sentinel_flag' for frontend
                            tool_args['sentinel_flag'] = tool_args.get('is_severe', False)
                            
                            return tool_args

            # Fallback if the agent talked but didn't act
            print(f"⚠️ Agent response text: {result.text}")
            return None
            
        except Exception as e:
            print(f"❌ ADK Error: {e}")
            raise e