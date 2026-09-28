import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from multiprocessing import Pool
from process_restaurant import process_restaurant
import json
import argparse
from pathlib import Path
from functools import partial

def parse_args():
    parser = argparse.ArgumentParser(
        description="JSONL 음식점 목록의 메뉴와 리뷰를 크롤링합니다."
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="크롤링할 음식점 JSONL 파일 (collect_restaurants.py 결과)",
    )
    parser.add_argument("--limit", type=int, help="이번 실행에서 처리할 최대 개수")
    parser.add_argument("--workers", type=int, default=2, help="동시 Chrome 프로세스 수")
    parser.add_argument(
        "--recrawl-existing",
        action="store_true",
        help="DB에 이미 존재하는 식당도 리뷰와 메뉴를 다시 수집",
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    with args.input.expanduser().resolve().open("r", encoding="utf-8") as f:
        unique_restaurants = [json.loads(line.strip()) for line in f]
    if args.limit:
        unique_restaurants = unique_restaurants[:args.limit]
    total = len(unique_restaurants)
    print(f"📦 처리할 식당 수: {len(unique_restaurants)}")
    
    worker = partial(process_restaurant, recrawl_existing=args.recrawl_existing)
    with Pool(processes=args.workers) as pool:
        for i, result in enumerate(pool.imap_unordered(worker, unique_restaurants), 1):
             print(f"[{i}/{total}] {result}")
    print("크롤링 완료")
