from bring_to_server import get_menu_texts
from fastapi import APIRouter
router = APIRouter()

@router.get("/restaurant/{place_id}/menus")
async def get_menu(user_id: str, place_id:int):
    menus =await get_menu_texts(user_id, place_id)
    return {"menus":menus}