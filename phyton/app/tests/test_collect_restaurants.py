import os

import pytest

from data.collect_restaurants import (
    Bounds,
    KakaoLocalClient,
    RestaurantCollector,
    generate_grid,
)


def restaurants(*ids):
    return [{"id": str(place_id)} for place_id in ids]


class RecordingSearch:
    """좌표·반경별로 정해진 결과를 돌려주고 호출 기록을 남기는 검색 함수."""

    def __init__(self, respond):
        self.respond = respond
        self.calls = []

    def __call__(self, lng, lat, radius):
        self.calls.append((lng, lat, radius))
        return self.respond(lng, lat, radius)


def test_bounds_from_string_parses_south_west_north_east():
    # Arrange
    text = "37.22,126.93,37.33,127.08"

    # Act
    bounds = Bounds.from_string(text)

    # Assert
    assert bounds == Bounds(south=37.22, west=126.93, north=37.33, east=127.08)


@pytest.mark.parametrize("text", ["37.33,126.93,37.22,127.08", "37.22,127.08,37.33,126.93", "37.22,126.93"])
def test_bounds_from_string_rejects_invalid_range(text):
    # Act & Assert
    with pytest.raises(ValueError):
        Bounds.from_string(text)


def test_generate_grid_covers_bounds_inclusively():
    # Arrange
    bounds = Bounds(south=37.0, west=127.0, north=37.009, east=127.011)

    # Act
    points = generate_grid(bounds, step_lat=0.0045, step_lng=0.0055)

    # Assert
    assert len(points) == 9
    assert points[0] == (37.0, 127.0)
    assert points[-1] == (37.009, 127.011)


def test_collect_removes_duplicate_restaurants_across_points():
    # Arrange
    bounds = Bounds(south=37.0, west=127.0, north=37.0, east=127.0055)
    search = RecordingSearch(lambda lng, lat, radius: restaurants(1, 2) if lng == 127.0 else restaurants(2, 3))
    collector = RestaurantCollector(search)

    # Act
    result = collector.collect(bounds, step_lat=0.0045, step_lng=0.0055, radius=500)

    # Assert
    assert [r["id"] for r in result] == ["1", "2", "3"]


def test_collect_does_not_subdivide_when_result_is_not_full():
    # Arrange
    bounds = Bounds(south=37.0, west=127.0, north=37.0, east=127.0)
    search = RecordingSearch(lambda lng, lat, radius: restaurants(*range(44)))
    collector = RestaurantCollector(search, max_results=45)

    # Act
    collector.collect(bounds, step_lat=0.0045, step_lng=0.0055, radius=500)

    # Assert
    assert len(search.calls) == 1


def test_collect_subdivides_full_result_into_four_smaller_searches():
    # Arrange
    bounds = Bounds(south=37.0, west=127.0, north=37.0, east=127.0)

    def respond(lng, lat, radius):
        if radius == 500:
            return restaurants(*range(45))
        return restaurants(f"{lat:.5f}-{lng:.5f}")

    search = RecordingSearch(respond)
    collector = RestaurantCollector(search, max_results=45, min_radius=100)

    # Act
    result = collector.collect(bounds, step_lat=0.0045, step_lng=0.0055, radius=500)

    # Assert
    sub_calls = [call for call in search.calls if call[2] == 250]
    assert len(sub_calls) == 4
    assert {(round(lat - 37.0, 6), round(lng - 127.0, 6)) for lng, lat, _ in sub_calls} == {
        (-0.001125, -0.001375), (-0.001125, 0.001375), (0.001125, -0.001375), (0.001125, 0.001375)
    }
    assert len(result) == 45 + 4


def test_collect_stops_subdividing_at_min_radius():
    # Arrange
    bounds = Bounds(south=37.0, west=127.0, north=37.0, east=127.0)
    search = RecordingSearch(lambda lng, lat, radius: restaurants(*range(45)))
    collector = RestaurantCollector(search, max_results=45, min_radius=200)

    # Act
    collector.collect(bounds, step_lat=0.0045, step_lng=0.0055, radius=500)

    # Assert
    assert min(radius for _, _, radius in search.calls) == 250
    assert len(search.calls) == 1 + 4


def test_kakao_client_requires_api_key():
    # Act & Assert
    with pytest.raises(ValueError, match="KAKAO_API_KEY"):
        KakaoLocalClient(api_key="")


@pytest.mark.skipif(not os.getenv("KAKAO_API_KEY"), reason="KAKAO_API_KEY가 없으면 실제 API E2E 테스트를 건너뜀")
def test_kakao_client_finds_restaurants_near_suwon_station():
    # Arrange
    client = KakaoLocalClient(api_key=os.environ["KAKAO_API_KEY"])

    # Act
    result = client.search_restaurants(lng=127.0000, lat=37.2664, radius=300)

    # Assert
    assert 0 < len(result) <= 45
    assert all(r["category_group_code"] == "FD6" for r in result)
    assert any("수원" in r["address_name"] for r in result)
