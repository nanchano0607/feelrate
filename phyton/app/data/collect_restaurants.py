import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

APP_DIR = Path(__file__).resolve().parents[1]
KAKAO_CATEGORY_URL = "https://dapi.kakao.com/v2/local/search/category.json"
RESTAURANT_CATEGORY = "FD6"
PAGE_SIZE = 15
MAX_PAGES = 3

Search = Callable[[float, float, int], list[dict]]


@dataclass(frozen=True)
class Bounds:
    south: float
    west: float
    north: float
    east: float

    @classmethod
    def from_string(cls, text: str) -> "Bounds":
        parts = [float(value) for value in text.split(",")]
        if len(parts) != 4:
            raise ValueError("범위는 '남,서,북,동' 4개 값이어야 합니다.")
        bounds = cls(*parts)
        if bounds.south > bounds.north or bounds.west > bounds.east:
            raise ValueError("남쪽/서쪽 값은 북쪽/동쪽 값보다 작아야 합니다.")
        return bounds


def generate_grid(bounds: Bounds, step_lat: float, step_lng: float) -> list[tuple[float, float]]:
    lat_count = int((bounds.north - bounds.south) / step_lat + 1e-9) + 1
    lng_count = int((bounds.east - bounds.west) / step_lng + 1e-9) + 1
    return [
        (round(bounds.south + i * step_lat, 6), round(bounds.west + j * step_lng, 6))
        for i in range(lat_count)
        for j in range(lng_count)
    ]


class KakaoLocalClient:
    def __init__(self, api_key: str, session: requests.Session | None = None):
        if not api_key:
            raise ValueError("KAKAO_API_KEY 환경변수가 설정되지 않았습니다.")
        self.session = session or requests.Session()
        self.session.headers["Authorization"] = f"KakaoAK {api_key}"

    def search_restaurants(self, lng: float, lat: float, radius: int) -> list[dict]:
        documents = []
        for page in range(1, MAX_PAGES + 1):
            response = self.session.get(KAKAO_CATEGORY_URL, params={
                "category_group_code": RESTAURANT_CATEGORY,
                "x": lng,
                "y": lat,
                "radius": radius,
                "size": PAGE_SIZE,
                "page": page,
                "sort": "distance",
            }, timeout=10)
            response.raise_for_status()
            body = response.json()
            documents.extend(body.get("documents", []))
            if body.get("meta", {}).get("is_end", True):
                break
        return documents


class RestaurantCollector:
    """격자 단위로 검색하고, 결과가 API 상한에 걸린 구역은 4등분해 다시 검색한다."""

    def __init__(self, search: Search, max_results: int = PAGE_SIZE * MAX_PAGES, min_radius: int = 100):
        self.search = search
        self.max_results = max_results
        self.min_radius = min_radius

    def collect(self, bounds: Bounds, step_lat: float, step_lng: float, radius: int) -> list[dict]:
        unique: dict[str, dict] = {}
        points = generate_grid(bounds, step_lat, step_lng)
        for index, (lat, lng) in enumerate(points, 1):
            for restaurant in self._search_cell(lat, lng, step_lat, step_lng, radius):
                unique.setdefault(restaurant["id"], restaurant)
            logger.info("[%d/%d] 누적 식당 수: %d", index, len(points), len(unique))
        return list(unique.values())

    def _search_cell(self, lat: float, lng: float, step_lat: float, step_lng: float, radius: int) -> list[dict]:
        results = self.search(lng, lat, radius)
        sub_radius = radius // 2
        if len(results) < self.max_results or sub_radius < self.min_radius:
            return results

        quarter_lat, quarter_lng = step_lat / 4, step_lng / 4
        for d_lat in (-quarter_lat, quarter_lat):
            for d_lng in (-quarter_lng, quarter_lng):
                results = results + self._search_cell(
                    round(lat + d_lat, 6), round(lng + d_lng, 6), step_lat / 2, step_lng / 2, sub_radius
                )
        return results


def parse_args():
    parser = argparse.ArgumentParser(description="Kakao Local API로 지정한 범위의 음식점 목록을 수집합니다.")
    parser.add_argument("--bounds", type=Bounds.from_string, required=True, help="수집 범위 '남,서,북,동' (예: 37.22,126.93,37.33,127.08)")
    parser.add_argument("--output", type=Path, required=True, help="결과 JSONL 파일 경로")
    parser.add_argument("--step-lat", type=float, default=0.0045, help="격자 위도 간격 (기본 약 500m)")
    parser.add_argument("--step-lng", type=float, default=0.0055, help="격자 경도 간격 (기본 약 500m)")
    parser.add_argument("--radius", type=int, default=500, help="격자 한 칸의 검색 반경(m)")
    return parser.parse_args()


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    load_dotenv(APP_DIR / ".env")
    args = parse_args()

    client = KakaoLocalClient(api_key=os.getenv("KAKAO_API_KEY", ""))
    restaurants = RestaurantCollector(client.search_restaurants).collect(
        args.bounds, args.step_lat, args.step_lng, args.radius
    )

    output = args.output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as file:
        for restaurant in restaurants:
            file.write(json.dumps(restaurant, ensure_ascii=False) + "\n")
    logger.info("수집 완료: %d곳 → %s", len(restaurants), output)


if __name__ == "__main__":
    sys.exit(main())
