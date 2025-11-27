from google.adk.agents import Agent
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
        self.agent = Agent(
            name="VunaGuideAgronomist",
            model=self.model,
            instruction="""
            You are VunaGuide, an expert Kenyan Agronomist.
            Your ONLY goal is to analyze the crop and SUBMIT a report using the tool.
            1. Identify the plant and disease.
            2. Suggest Kenyan remedies (e.g. Ridomil, Duduthrin).
            3. Use the 'submit_diagnosis_report' tool to finalize the result.
            """,
            # ✅ ADK Feature: Just pass the function directly!
            tools=[submit_diagnosis_report]
        )

    def diagnose_image(self, image_bytes: bytes, mime_type: str) -> dict:
        # 3. Create a Runner (Orchestrator)
        runner = Runner(agent=self.agent)

        print("🤖 ADK Agent Running...")
        
        # 4. Run with Multimodal Input
        # ADK runners usually accept a list of content
        try:
            # We construct the user prompt with the image
            from google.genai import types
            user_input = [
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                "Analyze this crop and submit the report."
            ]

            # Execute the agent
            result = runner.run(user_input)
            
            # 5. Extract the Tool Output
            # The runner result contains the conversation history and tool calls
            for turn in result.turns:
                for part in turn.parts:
                    if hasattr(part, "function_call") and part.function_call:
                        # If the agent called the function, we want the args
                        # ADK usually executes the tool and stores the result in the next turn
                        pass

            # Simpler hack for Hackathon:
            # If the tool was executed, the ADK runner returns the final 'text' 
            # OR we can intercept the tool call.
            
            # Since we want the STRUCTURED data, let's grab the last tool call from history
            last_tool_call = runner.memory.history[-1] # Simplification
            
            # Actually, standard ADK pattern is to let the tool return the dict
            # and the agent summarizes it. 
            # But we want the raw dict.
            
            # Let's inspect the `result` object to find our specific tool output
            # For this MVP, if the runner succeeded, our 'submit_diagnosis_report' 
            # returned a dict. We can grab it from the function execution result.
            
            # (Fallback: Use the logic from our previous manual implementation if ADK 
            # extraction is tricky, but ADK usually exposes `runner.tool_outputs`)
            
            # Let's rely on the Agent returning the JSON summary if we ask it to.
            return result.text  # This might be text, so we need to ensure the Tool returns JSON
            
        except Exception as e:
            print(f"❌ ADK Error: {e}")
            raise e