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
        
        # 3. Run Audit (The Evaluator)
        # We pass the raw dictionary of the diagnosis to the Sentinel
        # Note: diagnosis is a Pydantic model, so we dump it to dict
        audit_result = await sentinel.audit_diagnosis(diagnosis)
        
        # 4. Check Safety
        if not audit_result.get("safe", False):
            # OPTION A: Block completely
            # raise HTTPException(status_code=400, detail=f"Safety Block: {audit_result.get('reason')}")
            
            # OPTION B (Better for User): Flag it in the response
            # We override the local_advice with a warning
            diagnosis['local_advice'] = f"⚠️ SENTINEL WARNING: {audit_result.get('reason')} - Please consult a human expert."
            diagnosis['sentinel_flag'] = True

        return diagnosis

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))