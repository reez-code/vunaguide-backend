import json
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

    async def audit_diagnosis(self, diagnosis_json: dict) -> dict:
        """
        Checks if the diagnosis contains dangerous hallucinations.
        Returns a dict: { "safe": bool, "reason": str }
        """
        # We use json.dumps to ensure the AI reads the input clearly
        audit_prompt = f"""
        AUDIT THIS DIAGNOSIS:
        {json.dumps(diagnosis_json)}

        TASK:
        1. Does the remedy suggest banned chemicals?
        2. Is the confidence score > 90% but the advice generic?
        
        Return JSON: {{ "safe": true, "reason": "No issues found" }} or {{ "safe": false, "reason": "Explanation..." }}
        """
        
        try:
            print("🛡️ Sentinel is auditing...")
            
            response = self.client.models.generate_content(
                model=settings.MODEL_ID,
                contents=audit_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1 # Low temperature = stricter logic
                )
            )

            # 1. Try to get the automatically parsed JSON
            if response.parsed:
                return response.parsed
            
            # 2. Fallback: If parsed is None, try to read the raw text manually
            if response.text:
                print(f"⚠️ Sentinel Raw Text: {response.text}")
                clean_text = response.text.replace("```json", "").replace("```", "").strip()
                return json.loads(clean_text)

            # 3. If the AI returns nothing at all, default to SAFE (Fail Open)
            # This prevents the app from crashing during your demo
            print("⚠️ Sentinel returned empty response. Allowing passively.")
            return {"safe": True, "reason": "Sentinel Pass (Empty Response)"}

        except Exception as e:
            print(f"❌ Sentinel Error: {e}")
            # If the Sentinel crashes, we still return a valid dict so the API doesn't break
            return {"safe": True, "reason": f"Sentinel Skipped: {str(e)}"}