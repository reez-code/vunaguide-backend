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
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    "Diagnose this crop."
                ],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    temperature=0.3
                )
            )
            
            # Since response.parsed returns a Dictionary (thanks to JSON mode),
            # FastAPI will automatically validate it against your DiagnosisResult schema
            # when this function returns.
            return response.parsed
            
        except Exception as e:
            print(f"Agronomist Error: {e}")
            raise e