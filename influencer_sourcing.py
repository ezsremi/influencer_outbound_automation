import requests
import pandas as pd
import time
import os
from tqdm import tqdm
from datetime import datetime, timedelta, timezone

API_KEY = ""  # Replace with your key









KEYWORDS = ["Valorant", "Marvel Rivals", "GTAV"] #["Valorant", "Fortnite", "Marvel Rivals", "League of Legends", "GTAV", "Roblox"]
MAX_RESULTS_PER_KEYWORD = 15
SUBS_THRESHOLD = 50000
VIEWS_THRESHOLD = 15000
EXISTING_FILE = "influencers.csv"

def search_channels_by_keyword(keyword):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": API_KEY,
        "q": keyword,
        "type": "video",
        "part": "snippet",
        "maxResults": MAX_RESULTS_PER_KEYWORD,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    channels = {}
    for item in data.get("items", []):
        channel_id = item["snippet"]["channelId"]
        title = item["snippet"]["channelTitle"]
        channels[channel_id] = {
            "channelId": channel_id,
            "title": title,
            "keyword": keyword,
        }
    return list(channels.values())

def get_channel_stats(channel_ids):
    stats = []
    for i in range(0, len(channel_ids), 50):
        batch = channel_ids[i:i+50]
        url = "https://www.googleapis.com/youtube/v3/channels"
        params = {
            "key": API_KEY,
            "id": ",".join(batch),
            "part": "statistics,contentDetails",
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        for item in data.get("items", []):
            stats.append({
                "channelId": item["id"],
                "subscribers": int(item["statistics"].get("subscriberCount", 0)),
                "uploads_playlist": item["contentDetails"]["relatedPlaylists"]["uploads"]
            })
    return stats

def get_avg_views_from_video_ids(video_ids):
    if not video_ids:
        return 0

    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "statistics",
        "id": ",".join(video_ids),
        "key": API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        items = response.json().get("items", [])

        views = []
        for item in items:
            stats = item.get("statistics", {})
            view_count = int(stats.get("viewCount", 0))
            views.append(view_count)

        if views:
            return round(sum(views) / len(views))
        else:
            return 0

    except requests.exceptions.RequestException as e:
        print(f"[Error] Failed to fetch view stats for video IDs") #: {e}
        return 0


def get_recent_avg_views(playlist_id, retries=3, delay=5):
    one_month_ago = datetime.now(timezone.utc) - timedelta(days=30)
    video_ids = []
    next_page_token = None

    url = "https://www.googleapis.com/youtube/v3/playlistItems"

    while True:
        params = {
            "part": "contentDetails",
            "playlistId": playlist_id,
            "maxResults": 50,
            "pageToken": next_page_token,
            "key": API_KEY
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            for item in data.get("items", []):
                published_at = item["contentDetails"]["videoPublishedAt"]
                published_datetime = datetime.fromisoformat(published_at.replace("Z", "+00:00"))

                if published_datetime >= one_month_ago:
                    video_ids.append(item["contentDetails"]["videoId"])

            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break

        except requests.exceptions.RequestException as e:
            print(f"[Error] Failed to get playlist items: {e}")
            return None

    if not video_ids:
        return 0

    return get_avg_views_from_video_ids(video_ids)

def load_existing_data():
    if not os.path.exists(EXISTING_FILE):
        print(f"[Info] No existing file found at {EXISTING_FILE}. Starting fresh.")
        return pd.DataFrame()

    try:
        df = pd.read_csv(EXISTING_FILE, encoding="utf-8")
        print(f"[Info] Loaded {len(df)} existing entries.")
        return df
    except pd.errors.EmptyDataError:
        print(f"[Warning] Existing file {EXISTING_FILE} is empty. Starting fresh.")
        return pd.DataFrame()

def main():
    print("Starting influencer discovery...")

    all_channels = []
    for keyword in KEYWORDS:
        print(f"Searching for keyword: {keyword}")
        channels = search_channels_by_keyword(keyword)
        all_channels.extend(channels)
        time.sleep(1)

    df = pd.DataFrame(all_channels).drop_duplicates("channelId")

    print(f"Found {len(df)} unique channels. Fetching stats...")

    # Fetch channel stats with progress bar
    channel_ids = df["channelId"].tolist()
    stats = []
    for idx, batch_start in enumerate(range(0, len(channel_ids), 50)):
        batch = channel_ids[batch_start:batch_start + 50]
        # Add progress bar for batches of 50
        print(f"  → Processing batch {idx + 1} of {((len(channel_ids) - 1) // 50) + 1}...")
        stats.extend(get_channel_stats(batch))
        time.sleep(1)

    stats_df = pd.DataFrame(stats)
    df = df.merge(stats_df, on="channelId")

    # Calculate avg views per channel with progress bar
    print("Calculating average views for recent videos...")
    avg_views_list = []
    for i, row in tqdm(df.iterrows(), total=len(df), desc="Calculating avg views", unit="channel"):
        avg_views = get_recent_avg_views(row["uploads_playlist"])
        avg_views_list.append(avg_views)
        time.sleep(1)

    df["avg_views"] = avg_views_list
    df['email'] = ''

    # Filter by
    filtered_df = df[(df["subscribers"] >= SUBS_THRESHOLD) | (df["avg_views"] >= VIEWS_THRESHOLD)].copy()
    filtered_df["channel_url"] = "https://www.youtube.com/channel/" + filtered_df["channelId"]

    print(f"{len(filtered_df)} channels matched criteria.")

    # Load and merge with existing
    existing_df = load_existing_data()
    combined = pd.concat([existing_df, filtered_df], ignore_index=True)
    combined.drop_duplicates(subset=["channelId"], inplace=True)
    combined.to_csv(EXISTING_FILE, index=False)

    print("Results saved to influencers.csv")

if __name__ == "__main__":
    main()