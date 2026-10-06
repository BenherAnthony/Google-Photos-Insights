import os
import csv
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = "gemini-3.5-flash"  # or gemini-3.8-flash if more stable

INPUT_FILE = "data/playstore_reviews.csv"
OUTPUT_FILE = "insights/playstore_insights.txt"

def load_reviews():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def generate_playstore_insights(reviews):
    # Filter to likely retrieval-related reviews using keywords
    keywords = [
        "can't find",
        "cannot find",
        "search not",
        "old photos",
        "remember",
        "retrieve",
        "find photo",
        "find my photo",
        "find my photos",
        "missing photos",
        "photos disappeared",
    ]

    filtered = []
    for r in reviews:
        text = (r.get("title", "") + " " + r.get("text", "")).lower()
        if any(k in text for k in keywords):
            filtered.append(r)

    # If still many, cap to a reasonable sample
    SAMPLE_SIZE = 120
    if len(filtered) > SAMPLE_SIZE:
        filtered = filtered[:SAMPLE_SIZE]

    # Build text representation of reviews
    lines = []
    for i, r in enumerate(filtered):
        review_id = r.get("id", f"play_{i}")
        url = r.get("url", "")
        title = r.get("title", "") or ""
        review_text = r.get("text", "")
        lines.append(
            f"[{i}] ID: {review_id}\nURL: {url}\nTitle: {title}\nText: {review_text}\n"
        )

    reviews_text = "\n\n".join(lines)

    prompt = f"""
You are analyzing user reviews about Google Photos to understand **vaguely remembered photo retrieval** problems.

Below are reviews from the Google Play Store. Focus only on the ones where users are trying to find a photo they remember but cannot precisely describe.

Your task:
1. Identify the most common types of vaguely-remembered retrieval scenarios.
2. Summarize what users typically remember (e.g., trip, person, object, approximate time).
3. Summarize what they typically cannot recall (e.g., exact date, location name, filename).
4. Summarize emotional patterns (e.g., frustration, confusion, disappointment).
5. Ignore generic complaints about storage, syncing, UI, crashes, etc.

Return a structured insight summary in plain text with sections:
- Top retrieval scenarios
- What users typically remember
- What users typically miss
- Emotional patterns

IMPORTANT:
- When you mention an example or pattern, include 1–3 example review IDs in square brackets, like [play_abc123], [play_xyz789].
- Use the "id" field from each review when referencing examples.
- Also include the URL for at least some of the examples, like [play_abc123](http://...).
- Keep the main output as a concise summary; references should be brief and inline.

Here are the reviews:

{reviews_text}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    return response.text

def main():
    reviews = load_reviews()
    insights = generate_playstore_insights(reviews)
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(insights)
    print(f"Play Store insights saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()