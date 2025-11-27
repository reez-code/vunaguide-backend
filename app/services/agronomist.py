import json
from google import genai
from google.genai import types
from app.core import settings
from app.schemas import DiagnosisResult

class AgronomistService:
    def __init__(self):
        self.client = genai.Client(
            vertexai=True, 
            project=settings.GOOGLE_CLOUD_PROJECT, 
            location=settings.LOCATION
        )
        self.model = settings.MODEL_ID

    def diagnose_image(self, image_bytes: bytes, mime_type: str) -> DiagnosisResult:
        system_prompt = """
        You are VunaGuide, an expert Kenyan Agronomist.
        Analyze the image and return a JSON response matching this schema:
        {
            "plant_name": "String",
            "status": "Healthy/Diseased/Error",
            "disease_name": "String or null",
            "confidence_score": Float (0-100),
            "remedies": ["String", "String"],
            "local_advice": "Practical advice in English/Swahili context",
            "sentinel_flag": Boolean (True if disease is severe/contagious like MLN)
        }
        """
        
        try:
            print(f"🤖 Sending request to {self.model}...")
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    "Diagnose this crop."
                ],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    temperature=0.3,
                    # 👇 DISABLE SAFETY FILTERS (Critical for disease images)
                    safety_settings=[
                        types.SafetySetting(
                            category="HARM_CATEGORY_DANGEROUS_CONTENT",
                            threshold="BLOCK_ONLY_HIGH"
                        ),
                        types.SafetySetting(
                            category="HARM_CATEGORY_HARASSMENT",
                            threshold="BLOCK_ONLY_HIGH"
                        ),
                        types.SafetySetting(
                            category="HARM_CATEGORY_HATE_SPEECH",
                            threshold="BLOCK_ONLY_HIGH"
                        ),
                        types.SafetySetting(
                            category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                            threshold="BLOCK_ONLY_HIGH"
                        ),
                    ]
                )
            )

            # 👇 DEBUG: Print what the AI actually said
            print(f"📝 Raw AI Response: {response.text}")

            # If the auto-parser works, great.
            if response.parsed:
                return response.parsed
            
            # If not, try to parse the text manually
            if response.text:
                clean_text = response.text.replace("```json", "").replace("```", "").strip()
                return json.loads(clean_text)

            return None
            
        except Exception as e:
            print(f"❌ Agronomist Error: {e}")
            # If it's a validation error, we still want to see the raw text if possible
            raise e