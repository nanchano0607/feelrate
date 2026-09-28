import argparse
import json
import re
from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = APP_DIR / "backup_restaurants.jsonl"
DEFAULT_OUTPUT_DIR = APP_DIR / "data" / "filtered"


def parse_args():
    parser = argparse.ArgumentParser(
        description="백업 음식점 목록에서 특정 지역의 음식점만 추출합니다."
    )
    parser.add_argument("region", help="주소에서 찾을 지역명 (예: 강남구, 성수동)")
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="원본 JSONL 파일 경로",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="결과 JSONL 파일 경로 (기본: data/filtered/<지역명>.jsonl)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="저장할 최대 음식점 수",
    )
    return parser.parse_args()


def safe_filename(value: str) -> str:
    return re.sub(r"[^0-9A-Za-z가-힣_-]+", "_", value).strip("_")


def belongs_to_region(restaurant: dict, region: str) -> bool:
    addresses = (
        restaurant.get("address_name", ""),
        restaurant.get("road_address_name", ""),
    )
    return any(region in address for address in addresses)


def main():
    args = parse_args()
    input_path = args.input.expanduser().resolve()
    output_path = args.output or (
        DEFAULT_OUTPUT_DIR / f"restaurants_{safe_filename(args.region)}.jsonl"
    )
    output_path = output_path.expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    matched = []
    seen_place_ids = set()

    with input_path.open("r", encoding="utf-8") as source:
        for line_number, line in enumerate(source, 1):
            if not line.strip():
                continue

            try:
                restaurant = json.loads(line)
            except json.JSONDecodeError as error:
                print(f"[{line_number}행] JSON 파싱 실패: {error}")
                continue

            place_id = restaurant.get("id")
            if place_id in seen_place_ids or not belongs_to_region(restaurant, args.region):
                continue

            matched.append(restaurant)
            seen_place_ids.add(place_id)

            if args.limit and len(matched) >= args.limit:
                break

    with output_path.open("w", encoding="utf-8") as destination:
        for restaurant in matched:
            destination.write(json.dumps(restaurant, ensure_ascii=False) + "\n")

    print(f"지역: {args.region}")
    print(f"추출 개수: {len(matched)}")
    print(f"저장 파일: {output_path}")


if __name__ == "__main__":
    main()
