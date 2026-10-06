import os
import csv
from google_play_scraper import reviews_all, Sort
from dotenv import load_dotenv

load_dotenv()

APP_ID = "com.google.android.apps.photos"  # Google Photos
LANG = "en"
COUNTRY = "us"
SORT = Sort.MOST_RELEVANT
LIMIT = 120  # hard cap on number of reviews

OUTPUT_FILE = "data/playstore_reviews.csv"

def fetch_play_reviews():
    # Fetch a larger batch, then we'll truncate
    raw_result = reviews_all(
        APP_ID,
        lang=LANG,
        country=COUNTRY,
        sort=SORT,
        count=LIMIT * 2,  # ask for more, we'll cut down
    )

    # Enforce hard limit
    raw_result = raw_result[:LIMIT]

    rows = []
    for i, r in enumerate(raw_result):
        text = r.get("content", "") or r.get("text", "")
        if not text:
            continue

        review_id = r.get("reviewId", f"play_{i}")
        timestamp = r.get("at", "")

        rows.append({
            "id": f"play_{review_id}",
            "source": "play_store",
            "url": f"https://play.google.com/store/apps/details?id={APP_ID}&reviewId={review_id}",
            "timestamp": timestamp,
            "title": "",
            "text": text,
            "retrieval_related": "",
            "incident": "",
            "what_remember": "",
            "what_missed": "",
            "emotion": "",
        })

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    fieldnames = [
        "id","source","url","timestamp","title","text",
        "retrieval_related","incident","what_remember","what_missed","emotion"
    ]
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} Play Store reviews to {OUTPUT_FILE}")

if __name__ == "__main__":
    fetch_play_reviews()