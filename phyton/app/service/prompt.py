from langchain_core.prompts import PromptTemplate

# 출력 형식 예시에 구체적인 평점 숫자를 넣으면 모델이 그 값을 그대로 따라 하므로(앵커링) 설명만 둔다.
review_prompt_template = PromptTemplate.from_template("""
아래는 한 식당의 정보와 실제 방문자 리뷰입니다. 리뷰 내용만 근거로 분석하세요.

식당 이름: {name}
카카오맵 평점: {rating} (후기 {reviewCount}개)
식당 url: {url}

리뷰:
{review_text}

[AI 평점 기준] 0.0~5.0, 소수점 첫째 자리
- 맛, 서비스, 분위기, 가격 만족도에 대한 긍정·부정 언급을 종합해 판단합니다.
- 불만(맛, 양, 위생, 불친절 등)이 있으면 그 정도만큼 감점합니다.
- 카카오맵 평점을 그대로 따라 하지 말고, 리뷰 내용에서 드러난 만족도로 독립적으로 판단합니다.
- 리뷰가 적어 판단 근거가 부족하면 3.0 근처에서 보수적으로 매깁니다.

아래 JSON 형식으로만 답하세요. (값은 설명이며 예시 숫자가 아닙니다)
{{
  "name": "{name}",
  "url": "{url}",
  "reason": "리뷰에 근거한 추천 이유 1~2문장",
  "aiRating": <위 기준으로 계산한 0.0~5.0 숫자>,
  "realRating": {rating}
}}
""")

final_selection_prompt_template = PromptTemplate.from_template("""
다음은 여러 식당에 대한 분석 결과입니다. 사용자의 요청과 가장 잘 맞는 식당 5곳을 선택하여 JSON 배열로만 출력하세요.

[사용자 요청]
{user_input}

[식당 분석 결과]
{analyzed_results}

출력 형식 (값은 설명이며 예시 숫자가 아닙니다):
[
  {{
    "placeId": <분석 결과의 식당 ID>,
    "name": "<식당 이름>",
    "url": "<식당 url>",
    "reason": "<사용자 요청과 연결한 추천 이유>",
    "aiRating": <분석 결과의 aiRating>,
    "realRating": <분석 결과의 realRating>
  }}
]

조건:
- aiRating은 식당 분석 결과의 값을 그대로 옮기고, 새로 매기거나 바꾸지 마세요.
- 사용자의 요청에 적합한 식당 최대 5곳을 선택하세요.
- 사용자의 요청에 맞는식당이 5개보다 적은경우, 나머지 식당들 중 추천 할 만한 식당으로 5개를 채우시오.
- 반드시 JSON 배열만 출력하세요. 설명 문장, 코드블럭 없이.
- 5개보다 적다면 있는대로 추천하시오.
- 누락된 필드는 null 또는 생략해도 됩니다.
""")

context_prompt_template= PromptTemplate.from_template("""
    식당 이름: {name}
    실제 평점: {rating}
    리뷰 수: {reviewCount}

    아래는 이 식당에 대한 실제 리뷰입니다:
    ------------------------------
    {review_text}
    ------------------------------

    리뷰를 기반으로 이 식당이 다음과 같은 측면에서 어떤지 판단하세요:
    - 상황 (예: 혼밥, 회식, 가족 외식 등)
    - 분위기 (예: 조용한, 감성적인, 활기찬 등)
    - 목적 (예: 데이트, 가볍게 한잔 등)

    이 식당을 특정 상황/분위기/목적으로 추천할 수 있는 이유를 설명하고, AI 별점을 부여하세요.

    형식:
    식당 이름) - 상세점보):식당url
    추천이유)                                     
    AI평점) , 실제평점)
    """)

def build_review_prompt(restaurant: dict) -> str:
        reviews = restaurant.get("reviews", [])
        review_text = "\n".join([rev["text"] for rev in reviews])
        return review_prompt_template.format_prompt(
        name=restaurant.get("name", "이름 없음"),
        rating=restaurant.get("rating", 0.0),
        reviewCount=restaurant.get("reviewCount", 0),
        url=restaurant.get("url", "URL 없음"),
        review_text=review_text
    ).to_string()

def build_final_recommendation_prompt(analyzed_restaurants: list, input_text:str) -> str:
    text_blocks = []
    for r in analyzed_restaurants:
        name = r["name"]
        url = r["url"]
        place_id = r["placeId"]
        content = (
            r["llmResult"].content if hasattr(r["llmResult"], "content") else str(r["llmResult"])
        )
        text_blocks.append(f"식당 ID: {place_id}\n{name}\nURL: {url}\n{content.strip()}")

    combined = "\n\n".join(text_blocks)

    return final_selection_prompt_template.format_prompt(
        user_input = input_text,
        analyzed_results=combined
    ).to_string()


def build_context_prompt(restaurant:dict):
    reviews = restaurant.get("reviews", [])
    review_text = "\n".join([rev["text"] for rev in reviews])
    return context_prompt_template.format(
    name=restaurant.get("name", "이름 없음"),
    rating=restaurant.get("rating", 0.0),
    reviewCount=restaurant.get("reviewCount", 0),
    url=restaurant.get("url", "URL 없음"),
    review_text=review_text
    )