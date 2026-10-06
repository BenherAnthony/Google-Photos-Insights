import re
import streamlit as st
from pathlib import Path
import pandas as pd

# =============================================================
# 1. PATH CONFIGURATION
# =============================================================

DATA_DIR = Path("data")
INSIGHTS_DIR = Path("insights")

# Enriched CSVs
REDDIT_CSV = DATA_DIR / "reddit_reviews_enriched.csv"
PLAY_CSV = DATA_DIR / "playstore_reviews_enriched.csv"
HELP_CSV = DATA_DIR / "help_community_reviews_enriched.csv"

# Insight text files
REDDIT_INSIGHTS = INSIGHTS_DIR / "reddit_insights.txt"
PLAY_INSIGHTS = INSIGHTS_DIR / "playstore_insights.txt"
HELP_INSIGHTS = INSIGHTS_DIR / "help_community_insights.txt"
OVERALL_INSIGHTS = INSIGHTS_DIR / "overall_insights.txt"
PROPOSED_DIRECTION = INSIGHTS_DIR / "proposed_direction.txt"

# =============================================================
# 2. HELPER FUNCTIONS
# =============================================================

# Build a lookup from id -> url for clickable references
def build_id_url_lookup():
    lookup = {}
    for csv_path in [REDDIT_CSV, PLAY_CSV, HELP_CSV]:
        if not csv_path.exists():
            continue
        df = pd.read_csv(
            csv_path,
            delimiter=",",
            quotechar='"',
            quoting=1,
            engine="python",
            on_bad_lines="warn"
        )
        if "id" not in df.columns or "url" not in df.columns:
            continue
        for _, row in df.iterrows():
            rid = str(row["id"]).strip()
            url = str(row["url"]).strip()
            if rid and url and url.startswith("http"):
                lookup[rid] = url
    return lookup


# Turn [some_id] into clickable markdown links if we have a URL for it
def add_reference_links(text: str, id_url_lookup: dict) -> str:
    pattern = r"\[([^\]]+)\]"

    def replace_ref(match):
        ref_id = match.group(1)
        if ref_id in id_url_lookup:
            url = id_url_lookup[ref_id]
            return f"[{ref_id}]({url})"
        return match.group(0)

    return re.sub(pattern, replace_ref, text)


# Load raw text from an insight file
def load_insight_text(path: Path) -> str:
    if not path.exists():
        return f"_File not found: {path.name}_"
    return path.read_text(encoding="utf-8")


# Render an insight file with:
# - ## headers -> bigger headings
# - [Insight] / [Examples] blocks -> bulleted sentences with inline "Examples: [...]"
def render_insight_file(path: Path, id_url_lookup: dict):
    if not path.exists():
        st.warning(f"Insight file not found: {path.name}")
        return

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # Skip empty lines
        if not line:
            i += 1
            continue

        # Section headers: lines starting with ##
        if line.startswith("##"):
            header_text = line.lstrip("#").strip()
            st.markdown(f"### {header_text}")
            i += 1
            continue

        # Lines starting with '[' but not tags -> normal text (e.g. title line)
        if line.startswith("[") and line not in ("[Insight]", "[Examples]"):
            line_with_links = add_reference_links(line, id_url_lookup)
            st.markdown(line_with_links)
            i += 1
            continue

        # Insight block
        if line == "[Insight]":
            i += 1
            insight_lines = []
            while i < len(lines):
                cur = lines[i].strip()
                if cur in ("[Insight]", "[Examples]") or cur.startswith("##"):
                    break
                insight_lines.append(cur)
                i += 1

            insight_text = " ".join(l for l in insight_lines if l)
            if not insight_text:
                continue

            # Collect examples
            examples = []
            if i < len(lines) and lines[i].strip() == "[Examples]":
                i += 1
                while i < len(lines):
                    cur = lines[i].strip()
                    if cur in ("[Insight]", "[Examples]") or cur.startswith("##"):
                        break
                    if cur.startswith("[") and cur.endswith("]"):
                        examples.append(cur[1:-1])  # store without brackets
                    i += 1

            # Render insight sentence + inline examples
            if examples:
                examples_str = ", ".join(f"[{ex}]" for ex in examples)
                if not insight_text.startswith("- "):
                    insight_text = f"- {insight_text}"
                full_line = f"{insight_text}  Examples: {examples_str}"
                st.markdown(full_line)
            else:
                if not insight_text.startswith("- "):
                    insight_text = f"- {insight_text}"
                st.markdown(insight_text)

            continue

        # Any other line -> render as normal text
        line_with_links = add_reference_links(line, id_url_lookup)
        st.markdown(line_with_links)
        i += 1


# Render a source tab (Reddit / Play / Help) with:
# - Search box
# - Collapsible enriched table (filtered by search)
# - Insights summary using render_insight_file
def render_source_tab_with_search(
    header_title: str,
    csv_path: Path,
    insights_path: Path,
    id_url_lookup: dict
):
    st.header(header_title)

    # Load data
    if not csv_path.exists():
        st.warning(f"{csv_path.name} not found.")
        df = None
    else:
        df = pd.read_csv(
            csv_path,
            delimiter=",",
            quotechar='"',
            quoting=1,
            engine="python",
            on_bad_lines="warn"
        )

    # Search box for raw data
    search_query = st.text_input(
        "Search raw data (by ID, text, incident, etc.) - To clear search, just enter an empty string",
        key=f"search_{csv_path.name}"
    )

    with st.expander("Raw data (enriched)"):
        if df is not None:
            if search_query.strip():
                # Filter across all columns (case-insensitive)
                mask = df.apply(
                    lambda row: row.astype(str).str.contains(search_query, case=False, na=False).any(),
                    axis=1
                )
                df_filtered = df[mask]
                st.info(f"Showing {len(df_filtered)} of {len(df)} rows matching '{search_query}'")
                st.dataframe(df_filtered, use_container_width=True)
            else:
                st.dataframe(df, use_container_width=True)
        else:
            st.warning("No data available.")

    st.subheader("Insights Summary")
    render_insight_file(insights_path, id_url_lookup)


# =============================================================
# 3. PAGE CONFIG & GLOBAL SETUP
# =============================================================

st.set_page_config(
    page_title="Google Photos Retrieval Insights",
    layout="wide",
)

st.title("Google Photos — Vaguely Remembered Retrieval Insights")

# Build id -> url lookup for reference links
id_url_lookup = build_id_url_lookup()

# =============================================================
# 4. TABS DEFINITION
# =============================================================

tabs = st.tabs([
    "Overall Insights",
    "Reddit",
    "Play Store",
    "Help Community",
    "Proposed direction",
    "Pipeline architecture"
])

# -------------------------------------------------------------
# Tab 1: Overall Insights (cross-source narrative, no examples)
# -------------------------------------------------------------
with tabs[0]:
    st.header("Overall Insights (Cross-source)")

    overall_raw = load_insight_text(OVERALL_INSIGHTS)
    overall_with_links = add_reference_links(overall_raw, id_url_lookup)
    st.markdown(overall_with_links)

# -------------------------------------------------------------
# Tab 2: Reddit
# -------------------------------------------------------------
with tabs[1]:
    render_source_tab_with_search("Reddit Insights", REDDIT_CSV, REDDIT_INSIGHTS, id_url_lookup)

# -------------------------------------------------------------
# Tab 3: Play Store
# -------------------------------------------------------------
with tabs[2]:
    render_source_tab_with_search("Play Store Insights", PLAY_CSV, PLAY_INSIGHTS, id_url_lookup)

# -------------------------------------------------------------
# Tab 4: Help Community
# -------------------------------------------------------------
with tabs[3]:
    render_source_tab_with_search("Help Community Insights", HELP_CSV, HELP_INSIGHTS, id_url_lookup)

# -------------------------------------------------------------
# Tab 5: Proposed direction (plain narrative)
# -------------------------------------------------------------
with tabs[4]:
    st.header("Proposed direction")

    proposed_raw = load_insight_text(PROPOSED_DIRECTION)
    proposed_with_links = add_reference_links(proposed_raw, id_url_lookup)
    st.markdown(proposed_with_links)

# -------------------------------------------------------------
# Tab 6: Pipeline architecture (JPG diagram)
# -------------------------------------------------------------
with tabs[5]:
    st.header("Pipeline architecture")

    st.markdown(
        """
        This diagram shows how raw user conversations are turned into insights:

        - Raw data from three sources → AI enrichment → AI‑generated insights per source  
        - Insights are then converged into overall cross‑source insights
        - NOTE : This tab showing outcome and proposed direction is merely a suggestion of an idea formed. Surveys, insights, and ideation is already over by this stage, which is why it is included here.   
        """
    )

    # Ensure your JPG file is named gemini-pipeline.jpg and sits next to app.py
    st.image("Frame.png", use_container_width=True)