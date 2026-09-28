import os
from functools import lru_cache

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"{name} 환경변수가 설정되지 않았습니다.")
    return value


@lru_cache(maxsize=1)
def get_llm() -> ChatGroq:
    return ChatGroq(
        model=_require_env("GROQ_MODEL"),
        api_key=_require_env("GROQ_API_KEY"),
    )
