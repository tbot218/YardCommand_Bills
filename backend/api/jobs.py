from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
def jobs_test():
    return {"message": "Jobs router working"}
