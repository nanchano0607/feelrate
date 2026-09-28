import requests
from my_token.token_storage import get_valid_access_token
import httpx
SPRING_SERVER = "http://localhost:8080"#"http://feelrate.shop:8080"

def bring_menu_filter_restaurants(user_id:str, keywords:list):
    url = f"{SPRING_SERVER}/api/restaurants/filter/menu"
    token=get_valid_access_token(user_id, f"{SPRING_SERVER}/api/token")
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {"keywords": keywords}
    response = requests.post(url, json = payload, headers = headers)
    response.raise_for_status()
    data = response.json()
    return {"restaurants": data} 



def bring_context_filter_restaurants(user_id:str, contexts:list):
    url = f"{SPRING_SERVER}/api/restaurants/filter/context"
    token=get_valid_access_token(user_id, f"{SPRING_SERVER}/api/token")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"keywords": contexts}
    response = requests.post(url, json = payload, headers = headers)
    response.raise_for_status()
    data = response.json()
    return {"restaurants": data} 

def bring_rating_count(user_id:str, placeIds:list):
    url = f"{SPRING_SERVER}/api/restaurants/ratingAndCount"
    token=get_valid_access_token(user_id, f"{SPRING_SERVER}/api/token")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(url, json = placeIds, headers = headers)
    response.raise_for_status()
    data = response.json()
    return {"restaurants": data} 

def bring_restaurants_list(user_id:str, placeIds:list):
    url = f"{SPRING_SERVER}/api/restaurants/restaurants"
    token=get_valid_access_token(user_id, f"{SPRING_SERVER}/api/token")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(url, json = placeIds, headers = headers)
    response.raise_for_status()
    data = response.json()
    return {"restaurants": data} 

async def get_menu_texts(user_id:str, place_id:int) -> list:
    url = f"{SPRING_SERVER}/api/restaurants/{place_id}/menus"
    token=get_valid_access_token(user_id, f"{SPRING_SERVER}/api/token")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            raw_texts = response.json()
            return raw_texts
    except httpx.RequestError as e:
        return [{"text": f"메뉴 텍스트 요청 실패: {e}"}]
    
async def get_reivew_texts(user_id:str, place_id:int) -> list:
    url = f"{SPRING_SERVER}/api/restaurants/{place_id}/reviews"
    token=get_valid_access_token(user_id, f"{SPRING_SERVER}/api/token")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            raw_texts = response.json()
            print(raw_texts)
            return raw_texts
    except httpx.RequestError as e:
        return [{"text": f"메뉴 텍스트 요청 실패: {e}"}]