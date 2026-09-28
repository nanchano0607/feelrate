import re

from service.prompt import build_final_recommendation_prompt, build_review_prompt, final_selection_prompt_template

FIXED_RATING_EXAMPLE = re.compile(r'"aiRating"\s*:\s*\d')

RESTAURANT = {
    "placeId": 504819250,
    "name": "두루정 수원인계점",
    "rating": 4.0,
    "reviewCount": 3,
    "url": "http://place.map.kakao.com/504819250",
    "reviews": [{"text": "고기가 질기고 밥이 적어요"}, {"text": "반찬 무한리필이라 괜찮아요"}],
}

ANALYZED = [
    {
        "placeId": 504819250,
        "name": "두루정 수원인계점",
        "url": "http://place.map.kakao.com/504819250",
        "llmResult": '{"name": "두루정 수원인계점", "reason": "반찬이 푸짐함", "aiRating": 3.2, "realRating": 4.0}',
    }
]


def test_review_prompt_has_no_fixed_rating_example():
    # Act
    prompt = build_review_prompt(RESTAURANT)

    # Assert
    assert not FIXED_RATING_EXAMPLE.search(prompt)


def test_review_prompt_contains_rating_criteria():
    # Act
    prompt = build_review_prompt(RESTAURANT)

    # Assert
    assert "AI 평점 기준" in prompt
    assert "감점" in prompt


def test_review_prompt_includes_restaurant_info_and_all_reviews():
    # Act
    prompt = build_review_prompt(RESTAURANT)

    # Assert
    for expected in ["두루정 수원인계점", "4.0", "후기 3개", RESTAURANT["url"], "고기가 질기고 밥이 적어요", "반찬 무한리필이라 괜찮아요"]:
        assert expected in prompt


def test_final_prompt_template_has_no_fixed_rating_example():
    # Arrange: 렌더링된 프롬프트에는 분석 결과의 실제 aiRating이 포함되므로 템플릿(형식 예시)만 검사한다
    template = final_selection_prompt_template.template

    # Act & Assert
    assert not FIXED_RATING_EXAMPLE.search(template)


def test_final_prompt_instructs_to_copy_analyzed_rating_and_includes_inputs():
    # Act
    prompt = build_final_recommendation_prompt(ANALYZED, "인계동 고깃집")

    # Assert
    assert "aiRating은 식당 분석 결과의 값을 그대로" in prompt
    assert "인계동 고깃집" in prompt
    assert "식당 ID: 504819250" in prompt
