from get_review_by_selenium import crawl_review, init_driver
from send_to_server import send_restaurant, restaurant_is_exist

def process_restaurant(r, recrawl_existing=False):
    place_id = r.get("id", "unknown")
    try:
        place_id = int(r["id"])
        exists = restaurant_is_exist(place_id)
        if exists and not recrawl_existing:
            return f"[{place_id}] 이미 존재하여 건너뜀"

        restaurant = {
            "place_id": place_id,
            "name": r.get("place_name", ""),
            "address": r.get("road_address_name"),
            "url": r.get("place_url", ""),
            "category": r.get("category_name", ""),
            "latitude": r.get("y"),
            "longitude": r.get("x")
        }

        if not exists:
            status, response = send_restaurant(restaurant)
            if status >= 400:
                return f"[{place_id}] 식당 저장 실패: {status} {response}"

        driver = init_driver()
        try:
            return crawl_review(driver, restaurant["url"], place_id)
        finally:
            driver.quit()

    except Exception as e:
        return f"[{place_id}] 오류 발생: {e!r}"
