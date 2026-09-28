from service.prompt import build_review_prompt, build_final_recommendation_prompt
from llm.llm_client import get_llm
import asyncio

async def call_llm(prompt: str):
    stream = get_llm().astream(prompt)
    result = ""
    async for chunk in stream:
        if chunk.content:
            result += chunk.content
    return result


async def analyze_restaurant(restaurant: dict) -> dict:
    prompt = build_review_prompt(restaurant)
    response =await call_llm(prompt)
    
    result = {
        "placeId": restaurant["placeId"],
        "name": restaurant["name"],
        "url": restaurant["url"],
        "llmResult": response
    }
    print(result)
    return result
async def run_llm_analysis(data: dict) -> list:
    restaurants = data.get("restaurants", [])
    print("---------------------------------------------")
    print(restaurants)
    if not isinstance(restaurants, list):
        raise ValueError("restaurants는 리스트여야 합니다.")

    tasks = [analyze_restaurant(r) for r in restaurants]
    return await asyncio.gather(*tasks)


async def get_final_recommendation(results: list, input_text:str) -> str:
    """
    전체 흐름: 개별 분석 → 종합 프롬프트 → 최종 추천 생성
    """
    final_prompt = build_final_recommendation_prompt(results, input_text)
    return await call_llm(final_prompt)
