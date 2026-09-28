import logging

from agent.langGraphRunner import run_recommendation_pipeline
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from groq import NotFoundError, RateLimitError

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/start-recommendation")
async def start_recommendation(user_id: str, user_input:str):
    state = {
        "user_id": user_id,
        "user_input":user_input
    }
    try:
        return await run_recommendation_pipeline(state)
    except RateLimitError:
        logger.warning("Groq API 요청 한도 초과")
        return JSONResponse(
            status_code=429,
            content={"error": "LLM API 요청 한도를 초과했습니다. 잠시 후 다시 시도해 주세요."},
        )
    except NotFoundError as error:
        logger.error("Groq 모델 설정 오류: %s", error)
        return JSONResponse(
            status_code=502,
            content={"error": f"LLM 모델 설정 오류: {error.message}"},
        )
    except Exception as error:
        logger.exception("추천 처리 오류")
        return JSONResponse(
            status_code=500,
            content={"error": f"추천 처리 중 오류가 발생했습니다: {error}"},
        )
