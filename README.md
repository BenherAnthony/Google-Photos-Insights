# Google Photos Retrieval Insights

This Streamlit app presents AI-powered insights from user conversations about retrieving vaguely remembered photos in Google Photos.

## Live App

[Open Insights Dashboard](https://ai-discovery-engine-for-statistician.streamlit.app/)

## What this app does

- Displays cross-source insights from:
  - Reddit (r/googlephotos)
  - Google Play Store reviews
  - Google Photos Help Community
- Shows enriched data tables with AI-extracted attributes such as:
  - Whether the post is retrieval-related
  - What users remember vs. forget
  - Emotional tone
  - Specific retrieval incidents and workarounds
- Summarizes overall patterns and pain points in retrieving vaguely remembered photos.
- Documents the proposed product direction based on these insights.

## Repository structure

- `app.py` – Streamlit app entry point  
- `data/` – Enriched CSV files for each source  
- `insights/` – AI-generated insight summaries and proposed direction  
- `scrapers/` – Scripts used to collect raw data (Reddit, Play Store, Help Community)  
- `scripts/` – Data enrichment and processing scripts  
- `Frame.png` – Pipeline architecture diagram shown in the app  

## Running locally

1. Clone the repo:
   ```bash
   git clone https://github.com/BenherAnthony/Google-Photos-Insights.git
   cd Google-Photos-Insights
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

4. Open the local URL shown in the terminal (usually `http://localhost:8501`).

## Notes

- The parsing and analysis pipeline is **not dynamic**.  
  New data does not automatically update the insights. To refresh insights, the data extraction and AI analysis must be re-run manually.

- **Help Community data** was scraped manually due to technical difficulties with automated scraping.  
  The dataset is a snapshot and may not reflect the very latest discussions.

## License

(Add your chosen license here, e.g. MIT, or remove this section if not applicable.)
