import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# YouTube API Key
API_KEY = "AIzaSyCW4Pj5h4SIId6v0yTJr9SaG9Wljwnvmms"

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# Streamlit App Title
st.title("YouTube Viral Topics Tool")

# Input Fields
days = st.number_input("Enter Days to Search (1-30):", min_value=1, max_value=30, value=5)
region = st.text_input("Enter Region Code (e.g., US, IN, PK):", value="US")
video_type = st.radio("Select Video Type:", ["All", "Shorts (<60s)", "Long (60s+)"])
min_views = st.number_input("Minimum Views Filter:", min_value=0, value=1000)

# Keywords
keywords = [
    "Affair Relationship Stories", "Reddit Update", "Reddit Relationship Advice", "Reddit Relationship",
    "Reddit Cheating", "AITA Update", "Open Marriage", "Open Relationship", "X BF Caught",
    "Stories Cheat", "X GF Reddit", "AskReddit Surviving Infidelity", "GurlCan Reddit",
    "Cheating Story Actually Happened", "Cheating Story Real", "True Cheating Story",
    "Reddit Cheating Story", "R/Surviving Infidelity", "Surviving Infidelity",
    "Reddit Marriage", "Wife Cheated I Can't Forgive", "Reddit AP", "Exposed Wife", "Cheat Exposed",
    "Human evolution in under 60s", "history facts that are actually completely wrong",
    "disturbing mythical creatures you're never heard of", "the deadliest weapons of every time period",
    "Sketch animated explainer about history", "True crime", "25 cracked cold case to sleep to",
    "25 murder case with shocking plot", "boring history", "boring history sleep",
    "Automotive", "Havey vehicles"
]

# Fetch Data Button
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
                "maxResults": 10,
                "regionCode": region,
                "key": API_KEY,
            }

            response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
            data = response.json()

            if "items" not in data or not data["items"]:
                continue

            videos = data["items"]
            video_ids = [v["id"]["videoId"] for v in videos if "id" in v and "videoId" in v["id"]]
            channel_ids = [v["snippet"]["channelId"] for v in videos if "snippet" in v and "channelId" in v["snippet"]]

            if not video_ids or not channel_ids:
                continue

            # Video Stats
            stats_params = {"part": "statistics,contentDetails", "id": ",".join(video_ids), "key": API_KEY}
            stats_response = requests.get(YOUTUBE_VIDEO_URL, params=stats_params).json()

            # Channel Stats
            channel_params = {"part": "statistics", "id": ",".join(channel_ids), "key": API_KEY}
            channel_response = requests.get(YOUTUBE_CHANNEL_URL, params=channel_params).json()

            if "items" not in stats_response or "items" not in channel_response:
                continue

            stats = stats_response["items"]
            channels = channel_response["items"]

            for video, stat, channel in zip(videos, stats, channels):
                title = video["snippet"].get("title", "N/A")
                description = video["snippet"].get("description", "")[:200]
                video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
                views = int(stat["statistics"].get("viewCount", 0))
                subs = int(channel["statistics"].get("subscriberCount", 0))

                # Shorts vs Long filter
                duration = stat["contentDetails"].get("duration", "")
                is_short = "PT" in duration and "M" not in duration and "H" not in duration

                if video_type == "Shorts (<60s)" and not is_short:
                    continue
                if video_type == "Long (60s+)" and is_short:
                    continue

                # Minimum views filter
                if views < min_views:
                    continue

                # Subscriber filter
                if subs < 3000:
                    all_results.append({
                        "Title": title,
                        "Description": description,
                        "URL": video_url,
                        "Views": views,
                        "Subscribers": subs
                    })

        # Display results
        if all_results:
            st.success(f"Found {len(all_results)} results!")
            df = pd.DataFrame(all_results)
            st.dataframe(df)

            # CSV Download
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("Download Results as CSV", csv, "youtube_results.csv", "text/csv")
        else:
            st.warning("No results matched your filters.")

    except Exception as e:
        st.error(f"Error: {e}")
