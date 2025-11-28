from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from app.services import ManagerService
from app.schemas import DiagnosisResult

router = APIRouter()

# Dependency Injection for the Manager
def get_manager():
    return ManagerService()

@router.post("/analyze", response_model=DiagnosisResult)
async def analyze_crop(
    file: UploadFile = File(None),  # Optional: User might just ask a question
    question: str = Form(None),     # Optional: User might just upload a photo
    manager: ManagerService = Depends(get_manager)
):
    # 1. Input Validation
    if not file and not question:
        raise HTTPException(
            status_code=400, 
            detail="Please provide an image for diagnosis OR a question for advice."
        )

    # 2. Process File (if present)
    image_bytes = None
    mime_type = None
    
    if file:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        image_bytes = await file.read()
        mime_type = file.content_type
    
    try:
        # 3. Delegate to Manager (Strict Mode Logic)
        # The Manager decides: "Image? -> Diagnose" OR "No Image? -> Chat"
        result = manager.process_request(
            image_bytes=image_bytes, 
            mime_type=mime_type, 
            user_text=question
        )
        
        if result is None:
             raise HTTPException(
                status_code=500, 
                detail="System Error: The Agent failed to produce a result."
            )
        
        # 4. Handle Errors from the Manager
        if result.get("error"):
            raise HTTPException(status_code=400, detail=result["error"])
            
        return result

    except Exception as e:
        print(f"❌ API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))