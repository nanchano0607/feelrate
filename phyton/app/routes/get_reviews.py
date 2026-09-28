from bring_to_server import get_reivew_texts
from fastapi import APIRouter
router = APIRouter()

@router.get("/restaurant/{place_id}/reviews")
async def get_review(user_id: str, place_id:int):
    review =await get_reivew_texts(user_id, place_id)
    return {"review":review}