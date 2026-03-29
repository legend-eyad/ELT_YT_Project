import requests
import json
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="./.env")

API_KEY = os.getenv("API_KEY")

CHANNEL_HANDLE = "MrBeast"
maxResults = 50

print(API_KEY)

def get_playlist_id():

    try:
        url = f'https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}'

        response = requests.get(url)
        
        response.raise_for_status()

        data = response.json()
        # print(json.dumps(data, indent=4))

        channel_items = data["items"][0]
        channel_playlist_id = channel_items["contentDetails"]["relatedPlaylists"]["uploads"]
        # print(channel_playlist_id)
        return channel_playlist_id
    except requests.exceptions.RequestException as e:
        print(e)


def get_video_id(playlistId):
    videoIds = []
    base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={maxResults}&playlistId={playlistId}&key={API_KEY}"
    nextPageToken = None

    try:
        while True:

            url = base_url
            if nextPageToken:
                url+=f"&pageToken={nextPageToken}" 
        
            response = requests.get(url)
            response.raise_for_status()

            data = response.json()
            for item in data.get('items', []) :
                videoID = item["contentDetails"]["videoId"]
                videoIds.append(videoID)
            
            nextPageToken = data.get("nextPageToken")
            print("Next token:", nextPageToken)
            
            if not nextPageToken:
                break
        
    except requests.exceptions.RequestException as e:
        print(e)

    return videoIds





def get_videos_details(video_ids):

    extracted_data = []

    def batch_ls(video_id_list, batch_size):
        for video_id in range(0, len(video_id_list), batch_size):
            yield video_id_list[video_id : video_id + batch_size]

    for batch in batch_ls(video_ids, maxResults):

        video_id_str = "&id=".join(batch)
        url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={video_id_str}&key={API_KEY}"

        try: 
            response = requests.get(url)
            response.raise_for_status()

            data = response.json()

            

            for item in data.get("items", []):
                video_id = item["id"]
                snippet = item["snippet"]
                contentDetails = item["contentDetails"]
                statistics = item["statistics"]

                video_data = {

                "id" : video_id,
                "title" : snippet["title"],
                "publishedAt" : snippet["publishedAt"],
                "duration" : contentDetails["duration"],
                "viewCount" : statistics.get("viewCount", None),
                "likeCount" : statistics.get("likeCount", None),
                "commentCount": statistics.get("viewCount", None),

                }
                extracted_data.append(video_data)
        


        except requests.exceptions.RequestException() as e:
            print(e)

    print(len(extracted_data))
    return extracted_data


if __name__ == "__main__":
    playlistId = get_playlist_id()
    video_ids = get_video_id(playlistId)
    get_videos_details(video_ids)
        

