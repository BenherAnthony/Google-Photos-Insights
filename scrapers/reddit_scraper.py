import os
import csv
import praw
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT"),
)

SUBREDDIT = "googlephotos"
SEARCH_QUERIES = [
    "can't find photo",
    "search not working",
    "old photos",
    "remember photo but can't find",
    "retrieve photo",
]

LIMIT_PER_QUERY = 40  # adjust to get ~100 total posts

OUTPUT_FILE = "data/reddit_reviews.csv"

def fetch_reddit_posts():
    seen_ids = set()
    rows = []

    subreddit = reddit.subreddit(SUBREDDIT)

    for query in SEARCH_QUERIES:
        for submission in subreddit.search(query, limit=LIMIT_PER_QUERY, sort="relevance"):
            if submission.id in seen_ids:
                continue
            seen_ids.add(submission.id)

            text = f"{submission.title}\n\n{submission.selftext}"
            rows.append({
                "id": f"reddit_{submission.id}",
                "source": "reddit",
                "url": submission.url,
                "timestamp": datetime.utcfromtimestamp(submission.created_utc).isoformat(),
                "title": submission.title,
                "text": text,
                "retrieval_related": "",
                "incident": "",
                "what_remember": "",
                "what_missed": "",
                "emotion": "",
            })

            if len(rows) >= 150:  # safety cap
                break
        if len(rows) >= 150:
            break

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    fieldnames = [
        "id","source","url","timestamp","title","text",
        "retrieval_related","incident","what_remember","what_missed","emotion"
    ]
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} Reddit posts to {OUTPUT_FILE}")

if __name__ == "__main__":
    fetch_reddit_posts()