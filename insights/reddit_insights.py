import os
import csv
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = "gemini-3.5-flash"

INPUT_FILE = "data/reddit_reviews.csv"
OUTPUT_FILE = "insights/reddit_insights.txt"

def load_posts():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def generate_reddit_insights(posts):
    # Filter to likely retrieval-related posts using keywords
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
    ]

    filtered = []
    for p in posts:
        text = (p.get("title", "") + " " + p.get("text", "")).lower()
        if any(k in text for k in keywords):
            filtered.append(p)

    # Build text representation of posts
    lines = []
    for i, p in enumerate(filtered):
        title = p.get("title", "") or ""
        post_text = p.get("text", "")
        post_id = p.get("id", "")
        url = p.get("url", "")
        lines.append(
            f"[{i}] ID: {post_id}\nURL: {url}\nTitle: {title}\nText: {post_text}\n"
        )

    posts_text = "\n\n".join(lines)

    prompt = f"""
You are analyzing user posts about Google Photos to understand **vaguely remembered photo retrieval** problems.

Below are posts from Reddit (r/googlephotos). Focus only on the ones where users are trying to find a photo they remember but cannot precisely describe.

Your task:
1. Identify the most common types of vaguely-remembered retrieval scenarios.
2. Summarize what users typically remember (e.g., trip, person, object, approximate time).
3. Summarize what they typically cannot recall (e.g., exact date, location name, filename).
4. Summarize emotional patterns (e.g., frustration, confusion, disappointment).
5. Ignore generic complaints about storage, syncing, UI, etc.

Return a structured insight summary in plain text with sections:
- Top retrieval scenarios
- What users typically remember
- What users typically miss
- Emotional patterns

IMPORTANT:
- When you mention an example or pattern, include 1–3 example post IDs in square brackets, like [reddit_abc123], [reddit_xyz789].
- Use the "id" field from each post when referencing examples.
- Also include the URL for at least some of the examples, like [reddit_abc123](http://...).
- Keep the main output as a concise summary; references should be brief and inline.

Here are the posts:

{posts_text}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    return response.text

def main():
    posts = load_posts()
    insights = generate_reddit_insights(posts)
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(insights)
    print(f"Reddit insights saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()