import streamlit as st
import requests
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

# Updated Keywords List (Removed old Reddit/Cheating ones, Added new Pro-Level ones)
keywords = [

    # True Crime / Murder Cases
    "Cold case chronicles", "Unsolved murder mysteries", "Motive revealed true crime",
    "Crime incident analysis", "Victim’s story true crime", "Suspect interrogation breakdown",
    "Legal trial deep dive", "Disturbing crime case timeline",
    "Genetic Detective: Cold Cases Cracked", "First 24: Evidence Collection Failures",

    # History / Human Evolution / Weaponry
    "Human evolution in under 60s", "Human evolution in 60 seconds",
    "History facts that are actually completely wrong", "History facts you were told wrong",
    "Deadliest weapons of every time period", "Deadliest weapons through time",
    "Forgotten civilizations uncovered", "Animated history explainer",
    "Boring history", "Boring history made soothing",

    # Mythical Creatures / Dark Folklore
    "Unheard-of mythical beasts", "Disturbing mythical creatures you're never heard of",
    "Disturbing folklore creatures", "Ancient horror mythology",
    "Creepy legendary monsters", "Dark mythology stories you missed",

    # Explainer Animations / Sketch Videos
    "Sketch animated explainer about history", "Animated history explainers",
    "60-second explainer animations", "Motion-graphics educational videos",
    "Whiteboard sketch history", "Character-driven animated storytelling",
    "Visual storytelling via explainer video",

    # Automotive / Heavy Vehicles
    "Automotive", "Havey vehicles",
    "Evolution of heavy machinery", "Biggest heavy vehicles ever built",
    "History of military heavy vehicles", "Heavy vehicle documentary",
    "Heavy-duty truck evolution",

    # Sleep / Relaxation Content
    "Boring history sleep", "Boring history to lull you to sleep",
    "Sleep-friendly true crime narration", "Cold case stories for bedtime",
    "Relaxing mystery readings", "History sleep stories"
]

# Fetch Data Button
if st.button("Fetch Data"):
    try:
        # Calculate date range
        start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
        all_results = []

        # Iterate over keywords
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

            # Fetch video data
            response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
            data = response.json()

            if "items" not in data or not data["items"]:
                st.warning(f"No videos found for keyword: {keyword}")
                continue

            videos = data["items"]
            video_ids = [v["id"]["videoId"] for v in videos if "id" in v and "videoId" in v["id"]]
            channel_ids = [v["snippet"]["channelId"] for v in videos if "snippet" in v and "channelId" in v["snippet"]]

            if not video_ids or not channel_ids:
                st.warning(f"Skipping keyword: {keyword} due to missing data.")
                continue

            # Fetch video statistics
            stats_params = {"part": "statistics", "id": ",".join(video_ids), "key": API_KEY}
            stats_response = requests.get(YOUTUBE_VIDEO_URL, params=stats_params)
            stats_data = stats_response.json()

            if "items" not in stats_data or not stats_data["items"]:
                st.warning(f"No video stats found for keyword: {keyword}")
                continue

            # Fetch channel statistics
            channel_params = {"part": "statistics", "id": ",".join(channel_ids), "key": API_KEY}
            channel_response = requests.get(YOUTUBE_CHANNEL_URL, params=channel_params)
            channel_data = channel_response.json()

            if "items" not in channel_data or not channel_data["items"]:
                st.warning(f"No channel stats found for keyword: {keyword}")
                continue

            stats = stats_data["items"]
            channels = channel_data["items"]

            # Collect results
            for video, stat, channel in zip(videos, stats, channels):
                title = video["snippet"].get("title", "N/A")
                description = video["snippet"].get("description", "")[:200]
                video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
                views = int(stat["statistics"].get("viewCount", 0))
                subs = int(channel["statistics"].get("subscriberCount", 0))

                if subs < 3000:  # filter
                    all_results.append({
                        "Title": title,
                        "Description": description,
                        "URL": video_url,
                        "Views": views,
                        "Subscribers": subs
                    })

        # Display results
        if all_results:
            st.success(f"Found {len(all_results)} results across all keywords!")
            for result in all_results:
                st.markdown(
                    f"**Title:** {result['Title']}  \n"
                    f"**Description:** {result['Description']}  \n"
                    f"**URL:** [Watch Video]({result['URL']})  \n"
                    f"**Views:** {result['Views']}  \n"
                    f"**Subscribers:** {result['Subscribers']}"
                )
                st.write("---")
        else:
            st.warning("No results found with fewer than 3,000 subscribers.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
