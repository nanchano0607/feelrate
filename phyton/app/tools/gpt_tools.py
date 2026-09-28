import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import asyncio

from service.saveRestaurant_pipeline import (
    get_location_and_context,
    get_location_and_menu,
    get_coordinates_from_location,
    get_location_from_text,
    get_nearby_restaurants_DB
)
from bring_to_server import (
    bring_menu_filter_restaurants,
    bring_context_filter_restaurants,
    bring_restaurants_list,
    bring_rating_count
)
from llm.llm_call import run_llm_analysis, get_final_recommendation
from collections import Counter
from typing import TypedDict
from langgraph.graph import StateGraph
from service.saveRestaurant_pipeline import filtering_restaurant

# Define the state structure
class State(TypedDict):
    user_id:str
    user_input: str
    location: dict
    menu: dict
    context: dict
    candidates: dict
    restaurant_details: dict
    restaurant_aiRating: dict
    result: dict

# LangGraph-compatible tools

async def get_location_tool(user_id:str, input_text: str) -> dict:
    print("locationTool사용")
    location = await get_location_from_text(input_text)
    coords = await get_coordinates_from_location(location)
    if "error" in coords:
        return coords
    restaurants = get_nearby_restaurants_DB(user_id, coords["latitude"], coords["longitude"], radius=500)
    return restaurants


async def get_menu_tool(user_id:str ,input_text: str) -> dict:
    print("getmenuTool사용")
    keywords = await get_location_and_menu(input_text)
    restaurants = bring_menu_filter_restaurants(user_id, keywords)
    return restaurants


async def get_context_tool(user_id:str, input_text: str) -> dict:
    print("getcontextTool사용")
    contexts = await get_location_and_context(input_text)
    restaurants = bring_context_filter_restaurants(user_id, contexts)
    return restaurants

async def extract_all(user_id:str, input_text:str):
    location_task = get_location_tool(user_id, input_text)
    menu_task = get_menu_tool(user_id, input_text)
    context_task = get_context_tool(user_id, input_text)

    location, menu, context = await asyncio.gather(location_task, menu_task, context_task)
    return location, menu, context


def get_restaurant_info(user_id:str, restaurant_ids: dict) -> dict:
    print("교집합:")
    print(restaurant_ids)
    try:
        restaurants = restaurant_ids.get("restaurants", [])
        data = bring_rating_count(user_id, restaurants)
        filtered_restaurant = filtering_restaurant(data)
        result = bring_restaurants_list(user_id, filtered_restaurant)
        return result
    except Exception as e:
        return {"error": f"파싱 실패: {str(e)}"}


def intersection_restaurant(location:dict, menu:dict, context:dict):
    """
    여러 리스트에서 2번 이상 등장한 식당 ID만 반환하는 도구.
    """
    print("교집합함수 호출")
    try:
        location_ids = location.get("restaurants", [])
        menu_ids = menu.get("restaurants", [])
        context_ids = context.get("restaurants", [])

        strategies = [
            ("location_menu_context", set(location_ids) & set(menu_ids) & set(context_ids)),
            ("location_menu", set(location_ids) & set(menu_ids)),
            ("location_context", set(location_ids) & set(context_ids)),
            ("location", set(location_ids))  # fallback: 무조건 사용
        ]

        for key, result_set in strategies:
            if key != "location" and len(result_set) < 3:
                print(f"❌ {key}: {len(result_set)}개 → 패스")
                continue

            print(f"✅ {key} 사용 (총 {len(result_set)}개)")
            return {"restaurants": list(result_set), "source": key}

        print("⚠️ 추천 가능한 식당이 없습니다.")
        return {"restaurants": [], "source": "none"}

    except Exception as e:
        return {"error": str(e)}


async def final_recommend(restaurants_info: dict, input_text:str) -> dict:
    ai_rating = await run_llm_analysis(restaurants_info)
    result = await get_final_recommendation(ai_rating, input_text)
    print(result)
    return {"result":result,
            "aiRating":ai_rating
            }

graph_builder = StateGraph(State)

