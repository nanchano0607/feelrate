from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from send_to_server import send_restaurant_rating, send_reviews, send_menus

import time

MIN_REVIEW_LENGTH = 5
MORE_BUTTON_TEXT = "더보기"


def init_driver():
    options = Options()
    options.add_argument("--headless=new")  # Headless 모드
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)


class KakaoPlacePage:
    """카카오맵 장소 상세 페이지의 홈 탭에서 메뉴·평점·방문자 후기를 읽는다.

    평점과 후기 문단은 주변 랭킹·블로그 섹션에도 같은 클래스로 존재하므로 후기 섹션(.section_review)으로 범위를 제한한다.
    """

    MENU_ITEM = "#mainContent li"
    MENU_NAME = "strong.tit_item"
    MENU_PRICE = "p.desc_item"
    RATING = "#mainContent .section_review .head_total span.num_star"
    REVIEW_COUNT = "#mainContent .section_review .head_total strong.tit_total"
    REVIEW = "#mainContent .section_review p.desc_review"

    def __init__(self, driver):
        self.driver = driver

    def menus(self) -> list[dict]:
        menus = []
        for item in self.driver.find_elements(By.CSS_SELECTOR, self.MENU_ITEM):
            names = item.find_elements(By.CSS_SELECTOR, self.MENU_NAME)
            name = names[0].text.strip() if names else ""
            if name:
                prices = item.find_elements(By.CSS_SELECTOR, self.MENU_PRICE)
                menus.append({"name": name, "price": prices[0].text.strip() if prices else ""})
        return menus

    def rating(self) -> float:
        text = self._first_text(self.RATING)
        return float(text) if text else 0.0

    def review_count(self) -> int:
        digits = "".join(ch for ch in self._first_text(self.REVIEW_COUNT) if ch.isdigit())
        return int(digits) if digits else 0

    def reviews(self) -> list[dict]:
        texts = [self._clean(element.text) for element in self.driver.find_elements(By.CSS_SELECTOR, self.REVIEW)]
        unique = dict.fromkeys(text for text in texts if len(text) >= MIN_REVIEW_LENGTH)
        return [{"text": text} for text in unique]

    def _first_text(self, selector: str) -> str:
        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
        return elements[0].text.strip() if elements else ""

    @staticmethod
    def _clean(text: str) -> str:
        text = text.strip()
        if text.endswith(MORE_BUTTON_TEXT):
            text = text[: -len(MORE_BUTTON_TEXT)].rstrip()
        return text


def crawl_review(driver ,url: str, place_id: int):
    try:
        driver.get(url)
        time.sleep(2)

        page = KakaoPlacePage(driver)
        menus = page.menus()
        rating = page.rating()
        review_count = page.review_count()
        reviews = page.reviews()

        # 서버 전송
        rating_status, _ = send_restaurant_rating(place_id, rating, review_count)
        review_status, _ = send_reviews(place_id, reviews)
        menu_status, _ = send_menus(place_id, menus)

        return {
            "place_id": place_id,
            "rating": rating,
            "review_count": review_count,
            "saved_reviews": len(reviews),
            "saved_menus": len(menus),
            "status": [rating_status, review_status, menu_status],
        }

    except Exception as e:
        return {"place_id": place_id, "error": repr(e)}
