from fastapi import APIRouter
from enum import Enum

router = APIRouter()

@router.get("/live")
async def live():
    return {"status": "alive"}
