from google import genai
from google.genai import types
from app.core import settings

class SentinelService:
    def __init__(self):
        self.client = genai.Client(
            vertexai=True, 
            project=settings.GOOGLE_CLOUD_PROJECT, 
            location=settings.LOCATION
        )

    # Updated return type hint to 'dict' because response.parsed returns the JSON object
    async def audit_diagnosis(self, diagnosis_json: dict) -> dict:
        """
        Checks if the diagnosis contains dangerous hallucinations.
        Returns a dict: { "safe": bool, "reason": str }
        """
        audit_prompt = f"""
        AUDIT THIS DIAGNOSIS:
        {diagnosis_json}

        TASK:
        1. Does the remedy suggest banned chemicals?
        2. Is the confidence score > 90% but the advice generic?
        
        Return JSON: {{ "safe": true/false, "reason": "..." }}
        """
        
        try:
            response = self.client.models.generate_content(
                model=settings.MODEL_ID,
                contents=audit_prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return response.parsed
        except Exception as e:
            print(f"Sentinel Error: {e}")
            # Fallback to safe if Sentinel fails, or flag it as error
            return {"safe": False, "reason": f"Sentinel Audit Failed: {str(e)}"}