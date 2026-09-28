import os

from dotenv import load_dotenv
from my_token.token_storage import save_access_token
from fastapi.responses import RedirectResponse
from fastapi import APIRouter
import jwt

load_dotenv()
JWT_ALGORITHM = "HS256"
router = APIRouter()


def decode_user_id(token: str) -> str:
    """Spring이 발급한 JWT를 공유 비밀키(JWT_SECRET)로 검증하고 사용자 ID를 꺼낸다."""
    secret = os.getenv("JWT_SECRET")
    if not secret:
        raise ValueError("JWT_SECRET 환경변수가 설정되지 않았습니다.")
    payload = jwt.decode(token, secret, algorithms=[JWT_ALGORITHM])
    return str(payload.get("id"))


@router.get("/save-token")
async def save_token_from_redirect(token: str):
    """
    token만 받아 JWT 디코딩 → userId 추출 → Redis에 저장
    """
    try:
        user_id = decode_user_id(token)

        # Redis에 저장
        save_access_token(user_id, token)

        return RedirectResponse(
            url=
            f"http://localhost:5173/recommend?user_id={user_id}")
            #f"http://feelrate.shop/recommend?user_id={user_id}")

    except jwt.ExpiredSignatureError:
        return {"error": "만료된 토큰입니다"}
    except jwt.InvalidTokenError as e:
        return {"error": f"유효하지 않은 토큰입니다: {str(e)}"}
