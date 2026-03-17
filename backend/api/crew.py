# backend/api/crew.py

from fastapi import APIRouter

router = APIRouter()


# -----------------------------------
# SIMPLE TEST ENDPOINT (TEMPORARY)
# -----------------------------------
@router.get("/test")
def crew_test():
    return {"status": "ok", "message": "Crew endpoint working"}
