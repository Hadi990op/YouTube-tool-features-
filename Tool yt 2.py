import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# ==============================
# YouTube API Setup
# ==============================
API_KEY = "AIzaSyCW4Pj5h4SIId6v0yTJr9SaG9Wljwnvmms"
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# ==============================
# Streamlit UI
# ==============================
st.title("YouTube Viral Topics Tool")

# Input Fields
days = st.number_input("Enter Days to Search (1-30):", min_value=1, max_value=30, value=5)

# List of broader + new keywords
keywords = [
    # Old keywords
    "Affair Relationship Stories", "Reddit Update", "Reddit Relationship Advice", "Reddit Relationship",
    "Reddit Cheating", "AITA Update", "Open Marriage", "Open Relationship", "X BF Caught",
    "Stories Cheat", "X GF Reddit", "AskReddit Surviving Infidelity", "GurlCan Reddit",
    "Cheating Story Actually Happened", "Cheating Story Real", "True Cheating Story",
    "Reddit Cheating Story", "R/Surviving Infidelity", "Surviving Infidelity",
    "Reddit Marriage", "Wife Cheated I Can't Forgive", "Reddit AP", "Exposed Wife",
    "Cheat Exposed",

    # New keywords
    "Human evolution in under 60s", "History facts that are actually completely wrong",
    "Disturbing mythical creatures you're never heard of", "The deadliest weapons of every time period",
    "Sketch animated explainer about history", "True crime", "25 cracked cold case to sleep to",
    "25 murder case with shocking plot", "Boring history", "Boring history sleep",
    "Automotive", "Heavy vehicles"
]

# ==============================
# Fetch Data
# ==============================
if st.button("Fetch Data"):
    try:
        start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
        all_results = []

        for keyword in keywords:
            st.write(f"Searching for keyword: {keyword}")

            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": 5,
                "key": API_KEY,
            }

            response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
            data = response.json()

            if "items" not in data or not data["items"]:
                continue

            videos = data["items"]
            video_ids = [video["id"]["videoId"] for video in videos if "id" in video and "videoId" in video["id"]]
            channel_ids = [video["snippet"]["channelId"] for video in videos]

            if not video_ids or not channel_ids:
                continue

            # Video statistics
            stats_params = {"part": "statistics,snippet", "id": ",".join(video_ids), "key": API_KEY}
            stats_response = requests.get(YOUTUBE_VIDEO_URL, params=stats_params)
            stats_data = stats_response.json()

            # Channel statistics
            channel_params = {"part": "statistics", "id": ",".join(channel_ids), "key": API_KEY}
            channel_response = requests.get(YOUTUBE_CHANNEL_URL, params=channel_params)
            channel_data = channel_response.json()

            if "items" not in stats_data or "items" not in channel_data:
                continue

            stats = stats_data["items"]
            channels = channel_data["items"]

            # Channel subscribers lookup
            channel_lookup = {c["id"]: int(c["statistics"].get("subscriberCount", 0)) for c in channels}

            # Collect Results
            for stat in stats:
                video_id = stat["id"]
                snippet = stat["snippet"]
                channel_id = snippet["channelId"]
                title = snippet.get("title", "N/A")
                description = snippet.get("description", "")[:200]
                video_url = f"https://www.youtube.com/watch?v={video_id}"

                views = int(stat["statistics"].get("viewCount", 0))
                subs = channel_lookup.get(channel_id, 0)

                if subs < 3000:  # Only include small creators
                    all_results.append({
                        "Keyword": keyword,
                        "Title": title,
                        "Description": description,
                        "URL": video_url,
                        "Views": views,
                        "Subscribers": subs
                    })

        # Display results
        if all_results:
            st.success(f"Found {len(all_results)} results across all keywords!")
            df = pd.DataFrame(all_results)
            st.dataframe(df)
            st.download_button("Download CSV", df.to_csv(index=False), "viral_topics.csv", "text/csv")
        else:
            st.warning("No results found for your filters. Try increasing days.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
