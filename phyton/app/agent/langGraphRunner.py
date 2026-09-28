import os
import sys
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langgraph.graph import StateGraph, END
from langchain_core.runnables import Runnable
from typing import TypedDict
from langchain_core.runnables import RunnableLambda
from tools.gpt_tools import (
    get_location_tool,
    get_menu_tool,
    get_context_tool,
    intersection_restaurant,
    get_restaurant_info,
    final_recommend,
)

# ✅ 수정: 상태에 user_input 포함
class State(TypedDict):
    user_id:str
    user_input: str
    location: list
    menu: list
    context: list
    candidates: dict          
    restaurant_details: dict  
    restaurant_aiRating: dict
    result: dict
    end:bool

# 개별 노드 버전에서 사용할 위치 추출 노드.
# 사용자 문장에서 장소를 뽑고, 해당 위치 기준 식당 후보를 상태에 저장한다.
async def location_node(state: State) -> dict:
    location = await get_location_tool(state["user_id"],state["user_input"])
    print(location)
    return {
        "location": location,
        "user_input": state["user_input"]  # ← 추가
    }

# 개별 노드 버전에서 사용할 메뉴 추출 노드.
# 사용자 문장에서 음식/메뉴 키워드를 추출해 메뉴 기반 후보를 저장한다.
async def menu_node(state: State) -> dict:
    menu = await get_menu_tool(state["user_id"],state["user_input"])
    return {
        "menu": menu,
        "user_input": state["user_input"]  # ← 추가
    }

# 개별 노드 버전에서 사용할 분위기/상황 추출 노드.
# 예: 혼밥, 데이트, 조용한 분위기 같은 맥락 조건을 추출한다.
async def context_node(state: State) -> dict:
    context = await get_context_tool(state["user_id"],state["user_input"])
    return {
        "context": context,
        "user_input": state["user_input"]  # ← 추가
    }

# LangGraph의 실제 분기 함수.
# 분기 기준:
# 1) end == True  -> 추천을 계속할 수 없는 상태이므로 그래프 종료
# 2) end가 없거나 False -> 후보 교집합 계산 단계로 이동
# 즉, "조기 종료"와 "추천 계속 진행" 두 갈래로 나뉜다.
def next_tool_selector(state: dict) -> str:
    if state.get("end") is True:
        return END
    return "intersection_node"

# 그래프의 첫 진입 노드.
# 위치/메뉴/분위기 추출을 병렬로 실행한 뒤,
# 위치 기반 후보가 있는지 여부로 다음 분기를 결정한다.
async def extract_all(state: State) -> dict:
    try:
        location_task = get_location_tool(state["user_id"], state["user_input"])
        menu_task = get_menu_tool(state["user_id"], state["user_input"])
        context_task = get_context_tool(state["user_id"], state["user_input"])

        location, menu, context = await asyncio.gather(location_task, menu_task, context_task, return_exceptions=True)
        # 첫 번째 분기 조건:
        # 위치 기반 후보가 없으면 이후 교집합/상세조회/최종추천이 의미 없으므로
        # end=True 를 내려서 next_tool_selector가 END로 보내도록 한다.
        if not location.get("restaurants"):  # 또는 len(location["restaurants"]) == 0
            return {"end": True,
                    "result":"장소명과 함께 다시 입력하여 주세요"
                    }

        # 위치 후보가 있으면 추천을 계속 진행한다.
        # 이후 intersection_node에서 location/menu/context 세 결과를 함께 사용한다.
        return {
            "location": location,
            "menu": menu,
            "context": context
        }
    except Exception as e:
        print(f"❌ extract_all 에러 발생: {e}")
        return {"location": {}, "menu": {}, "context": {}, "error": str(e)}



async def intersection_node(state: State) -> dict:
    # 세 축의 후보(location, menu, context)를 비교해
    # 교집합 우선 전략으로 최종 후보군을 압축한다.
    candidates = intersection_restaurant(
        state["location"],
        state["menu"],
        state["context"]
    )
    return {"candidates": candidates}


async def detail_node(state: State) -> dict:
    # 압축된 후보군의 평점/리뷰 수/상세 정보를 조회해
    # LLM이 최종 판단할 수 있는 입력 데이터로 정리한다.
    details = get_restaurant_info(state["user_id"],state["candidates"])
    return {"restaurant_details": details}  # ✅ 키 이름 변경

async def final_node(state: State) -> dict:  
    # 후보 식당 리뷰를 LLM이 분석하고,
    # 사용자 요청과 가장 잘 맞는 최종 추천 결과를 생성한다.
    result = await final_recommend(state["restaurant_details"], state["user_input"])
    return {
        "result": result["result"],
        "restaurant_aiRating": result["aiRating"]
    }



# LangGraph 설정
graph_builder = StateGraph(State)

graph_builder.add_node("location_node", location_node)
graph_builder.add_node("menu_node", menu_node)
graph_builder.add_node("context_node", context_node)
graph_builder.add_node("intersection_node", intersection_node)
graph_builder.add_node("detail_node", detail_node)
graph_builder.add_node("final_node", final_node)
graph_builder.add_node("extract_filters", RunnableLambda(extract_all))


# 그래프 시작점:
# extract_filters에서 조건을 병렬 추출한 뒤
# next_tool_selector가 END 또는 intersection_node로 분기시킨다.
graph_builder.set_entry_point("extract_filters")

graph_builder.add_conditional_edges(
    "extract_filters",
    next_tool_selector 
)
# 분기 후에는 직렬 흐름으로 이어진다.
# intersection_node -> detail_node -> final_node -> END
graph_builder.add_edge("intersection_node", "detail_node")
graph_builder.add_edge("detail_node", "final_node")
graph_builder.add_edge("final_node", END)


# 실행 함수
async def run_recommendation_pipeline(state: dict) -> dict:
    graph = graph_builder.compile()
    result = await graph.ainvoke(state)
    return result
