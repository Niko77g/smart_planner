from fastapi import APIRouter

router = APIRouter(tags=["status"])

@router.get("/status")
def get_status():
    return {"status": "ok"}
