import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from groq import NotFoundError, RateLimitError

import routes.recommendation as recommendation


def groq_error(error_class, status_code: int):
    request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
    response = httpx.Response(status_code, request=request)
    return error_class("groq error", response=response, body=None)


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(recommendation.router)
    return TestClient(app)


def raise_on_pipeline(monkeypatch, error):
    async def failing_pipeline(state):
        raise error

    monkeypatch.setattr(recommendation, "run_recommendation_pipeline", failing_pipeline)


def test_rate_limit_error_returns_429(client, monkeypatch):
    # Arrange
    raise_on_pipeline(monkeypatch, groq_error(RateLimitError, 429))

    # Act
    response = client.get("/start-recommendation", params={"user_id": "1", "user_input": "강남역 파스타"})

    # Assert
    assert response.status_code == 429
    assert "한도" in response.json()["error"]


def test_model_not_found_error_returns_502(client, monkeypatch):
    # Arrange
    raise_on_pipeline(monkeypatch, groq_error(NotFoundError, 404))

    # Act
    response = client.get("/start-recommendation", params={"user_id": "1", "user_input": "강남역 파스타"})

    # Assert
    assert response.status_code == 502
    assert "모델" in response.json()["error"]


def test_missing_llm_config_returns_500_with_reason(client, monkeypatch):
    # Arrange
    raise_on_pipeline(monkeypatch, ValueError("GROQ_API_KEY 환경변수가 설정되지 않았습니다."))

    # Act
    response = client.get("/start-recommendation", params={"user_id": "1", "user_input": "강남역 파스타"})

    # Assert
    assert response.status_code == 500
    assert "GROQ_API_KEY" in response.json()["error"]
