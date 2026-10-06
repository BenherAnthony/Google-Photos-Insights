import os
import sys
import csv
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = "models/gemini-3.5-flash"

# -----------------------------
# Configuration
# -----------------------------
# Expected input columns
BASE_COLUMNS = [
    "id", "source", "url", "timestamp", "title", "text"
]

# Columns to add
ENRICH_COLUMNS = [
    "retrieval_related",  # "yes" | "no" | "unsure"
    "incident",           # 1–2 sentences describing the retrieval situation
    "what_remember",      # comma-separated short phrases
    "what_missed",        # comma-separated short phrases
    "emotion",            # 1–3 words
]


def load_posts(input_path: str):
    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def enrich_posts(posts):
    # Build JSON input for the LLM
    input_payload = [
        {
            "id": p["id"],
            "title": p["title"],
            "text": p["text"],
        }
        for p in posts
    ]

    prompt = f"""
You are a senior product researcher analyzing user feedback about Google Photos retrieval.

You will be given a list of posts in JSON format. Each item has:
- id
- title
- text

Your tasks:

1) For each post, decide if it is retrieval-related:
   - Set retrieval_related = "yes" if the post describes:
     * Trying to find/search/locate a specific photo, album, person, pet, or memory
     * Search not returning expected results
     * Photos missing when the user expects them to be findable
     * Navigation/organization changes that make finding photos harder (explicitly stated)
     * Inability to locate photos by caption, note, text-in-image, person, date, location, etc.
   - Set retrieval_related = "no" if it is purely about editing, UI aesthetics, backup speed, storage, printing, or general complaints with no mention of finding/locating photos.
   - Set retrieval_related = "unsure" if you cannot confidently decide.

2) For posts where retrieval_related = "yes", extract:
   - incident (1–2 sentences): brief description of the retrieval situation and what went wrong.
   - what_remember (list of short phrases): clues the user did have (e.g., "person (husband)", "trip to Goa", "café during vacation", "album name", "caption 'lock'", "text in screenshot").
   - what_missed (list of short phrases): key attributes the user could not recall or use (e.g., "exact date", "location name", "album", "filename", "exact keyword", "person's name in People search").
   - emotion (1–3 words): dominant emotion inferred from tone (e.g., "frustrated, anxious", "confused, disappointed", "angry, betrayed").

   For retrieval_related = "no" or "unsure", set:
   - incident = ""
   - what_remember = []
   - what_missed = []
   - emotion = ""

3) Return your result as a JSON array, where each item has:
   {{
     "id": "...",
     "retrieval_related": "yes|no|unsure",
     "incident": "...",
     "what_remember": ["...", "..."],
     "what_missed": ["...", "..."],
     "emotion": "..."
   }}

Do not include any extra text outside the JSON array.


Here are the posts:

{json.dumps(input_payload, ensure_ascii=False, indent=2)}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    results = json.loads(response.text.strip())
    result_map = {r["id"]: r for r in results}

    enriched = []
    for p in posts:
        r = result_map.get(p["id"], {})
        enriched.append(
            {
                "id": p["id"],
                "source": p.get("source", ""),
                "url": p.get("url", ""),
                "timestamp": p.get("timestamp", ""),
                "title": p.get("title", ""),
                "text": p.get("text", ""),
                "retrieval_related": r.get("retrieval_related", ""),
                "incident": r.get("incident", ""),
                "what_remember": "; ".join(r.get("what_remember", [])),
                "what_missed": "; ".join(r.get("what_missed", [])),
                "emotion": r.get("emotion", ""),
            }
        )
    return enriched


def save_enriched_csv(rows, output_path: str):
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    fieldnames = BASE_COLUMNS + ENRICH_COLUMNS
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    if len(sys.argv) != 3:
        print("Usage: python scripts/enrich_csv.py <input_csv> <output_csv>")
        print("Example: python scripts/enrich_csv.py data/reddit_reviews.csv data/reddit_reviews_analyzed.csv")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    print(f"Loading posts from {input_path}...")
    posts = load_posts(input_path)
    print(f"Loaded {len(posts)} posts.")

    print(f"Enriching posts with retrieval fields...")
    enriched = enrich_posts(posts)

    print(f"Saving enriched CSV to {output_path}...")
    save_enriched_csv(enriched, output_path)

    # Quick summary
    yes = sum(1 for r in enriched if r["retrieval_related"] == "yes")
    no = sum(1 for r in enriched if r["retrieval_related"] == "no")
    unsure = sum(1 for r in enriched if r["retrieval_related"] == "unsure")
    print(f"Done. retrieval_related: yes={yes}, no={no}, unsure={unsure}")


if __name__ == "__main__":
    main()