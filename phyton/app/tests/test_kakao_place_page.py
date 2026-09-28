from urllib.parse import quote

import pytest

from data.get_review_by_selenium import KakaoPlacePage, init_driver

# 2026-09 카카오맵 장소 상세 페이지 구조를 축약한 HTML.
# 평점(num_star)이 상단·후기 섹션·주변 랭킹에 모두 있고, 리뷰 문단(desc_review)은 방문자 후기와 블로그 섹션에 모두 있다.
PLACE_WITH_REVIEWS = """
<div id="mainContent">
  <div class="top_basic"><div class="info_main"><span class="starred_grade"><span class="num_star">4.5</span></span></div></div>
  <div class="section_comm">
    <ul>
      <li><strong class="tit_item">수제돈가스</strong><p class="desc_item">9,500원</p></li>
      <li><strong class="tit_item">치즈돈가스</strong></li>
    </ul>
  </div>
  <div class="section_comm section_review">
    <div class="group_total"><div class="head_total">
      <span class="starred_grade"><span class="num_star">4.0</span></span>
      <a class="link_reviewall"><strong class="tit_total">후기 1,234</strong></a>
    </div></div>
    <ul>
      <li><p class="desc_review">분위기가 조용해서 데이트하기 좋아요... 더보기</p></li>
      <li><p class="desc_review">분위기가 조용해서 데이트하기 좋아요... 더보기</p></li>
      <li><p class="desc_review">굿</p></li>
      <li><p class="desc_review">사장님이 친절하세요</p></li>
    </ul>
  </div>
  <div class="section_comm section_blog">
    <ul class="list_blog"><li><p class="desc_review">안녕하세요 여러분! 오늘은 맛집 소개</p></li></ul>
  </div>
  <div class="cont_tab"><ul class="list_ranking"><li><span class="num_star">3.9</span></li></ul></div>
</div>
"""

PLACE_WITHOUT_REVIEWS = """
<div id="mainContent">
  <div class="section_comm"><h3>방문 후기를 남겨주세요!</h3></div>
  <div class="cont_tab"><ul class="list_ranking"><li><span class="num_star">4.2</span></li></ul></div>
</div>
"""


@pytest.fixture(scope="module")
def driver():
    chrome = init_driver()
    yield chrome
    chrome.quit()


def open_page(driver, html: str) -> KakaoPlacePage:
    driver.get("data:text/html;charset=utf-8," + quote(html))
    return KakaoPlacePage(driver)


def test_rating_comes_from_review_section_not_nearby_ranking(driver):
    # Arrange
    page = open_page(driver, PLACE_WITH_REVIEWS)

    # Act
    rating = page.rating()

    # Assert
    assert rating == 4.0


def test_review_count_parses_number_with_comma(driver):
    # Arrange
    page = open_page(driver, PLACE_WITH_REVIEWS)

    # Act
    review_count = page.review_count()

    # Assert
    assert review_count == 1234


def test_place_without_reviews_has_zero_rating_even_if_ranking_has_stars(driver):
    # Arrange
    page = open_page(driver, PLACE_WITHOUT_REVIEWS)

    # Act & Assert
    assert page.rating() == 0.0
    assert page.review_count() == 0
    assert page.reviews() == []


def test_reviews_exclude_blog_and_short_duplicate_texts_and_strip_more_button(driver):
    # Arrange
    page = open_page(driver, PLACE_WITH_REVIEWS)

    # Act
    reviews = page.reviews()

    # Assert
    assert reviews == [
        {"text": "분위기가 조용해서 데이트하기 좋아요..."},
        {"text": "사장님이 친절하세요"},
    ]


def test_menus_collect_name_and_optional_price(driver):
    # Arrange
    page = open_page(driver, PLACE_WITH_REVIEWS)

    # Act
    menus = page.menus()

    # Assert
    assert menus == [
        {"name": "수제돈가스", "price": "9,500원"},
        {"name": "치즈돈가스", "price": ""},
    ]
