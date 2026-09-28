import pytest
from langchain_groq import ChatGroq

from llm.llm_client import get_llm


@pytest.fixture(autouse=True)
def clear_llm_cache():
    get_llm.cache_clear()
    yield
    get_llm.cache_clear()


def test_get_llm_raises_when_api_key_missing(monkeypatch):
    # Arrange
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setenv("GROQ_MODEL", "test-model")

    # Act & Assert
    with pytest.raises(ValueError, match="GROQ_API_KEY"):
        get_llm()


def test_get_llm_raises_when_model_missing(monkeypatch):
    # Arrange
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test")
    monkeypatch.delenv("GROQ_MODEL", raising=False)

    # Act & Assert
    with pytest.raises(ValueError, match="GROQ_MODEL"):
        get_llm()


def test_get_llm_returns_chatgroq_configured_from_env(monkeypatch):
    # Arrange
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test")
    monkeypatch.setenv("GROQ_MODEL", "test-model")

    # Act
    llm = get_llm()

    # Assert
    assert isinstance(llm, ChatGroq)
    assert llm.model_name == "test-model"


def test_get_llm_reuses_single_instance(monkeypatch):
    # Arrange
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test")
    monkeypatch.setenv("GROQ_MODEL", "test-model")

    # Act
    first = get_llm()
    second = get_llm()

    # Assert
    assert first is second
