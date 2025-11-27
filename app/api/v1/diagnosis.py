from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.services import AgronomistService, SentinelService
from app.schemas import DiagnosisResult

router = APIRouter()

# Dependency Injection helpers
def get_agronomist():
    return AgronomistService()

def get_sentinel():
    return SentinelService()

@router.post("/analyze", response_model=DiagnosisResult)
async def analyze_crop(
    file: UploadFile = File(...),
    agronomist: AgronomistService = Depends(get_agronomist),
    sentinel: SentinelService = Depends(get_sentinel)
):
    # 1. Validate File
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    contents = await file.read()
    
    try:
        # 2. Get Diagnosis (The Agent)
        diagnosis = agronomist.diagnose_image(contents, file.content_type)
        
        # 🛑 FIX: Check if AI failed to generate JSON
        if diagnosis is None:
            raise HTTPException(
                status_code=500, 
                detail="AI returned no data. It might have been blocked or failed to generate JSON."
            )

        # 3. Run Audit (The Evaluator)
        audit_result = await sentinel.audit_diagnosis(diagnosis)
        
        # 4. Check Safety
        if not audit_result.get("safe", False):
            # We explicitly modify the dict here.
            # Since diagnosis is not None (checked above), this will now work.
            reason = audit_result.get("reason", "Unknown Safety Issue")
            diagnosis['local_advice'] = f"⚠️ SENTINEL WARNING: {reason} - Please consult a human expert."
            diagnosis['sentinel_flag'] = True

        return diagnosis

    except Exception as e:
        # Print the error to your terminal so you can see what happened
        print(f"❌ API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))