## The following script allows you do download all youtube transcription in a single playlist
## To run, you will neeed a youtube playlist id.
## it will look like this https://www.youtube.com/watch?v={playlist-id}&list=PLAEQD0ULngi67rwmhrkNjMZKvyCReqDV4
## you'lll also need your YouTube API key https://developers.google.com/youtube/v3/getting-started

##This will create a csv that contains the video information as well as the transcript, if avaialble


import requests
import json
import pandas as pd
from pandas.io.json import json_normalize #package for flattening json in pandas df
from xml.etree import ElementTree
from pandas.io.json import json_normalize
import sys

YT_API_KEY = ''
playlist_id = ''
results = []

def load_playlist(api_key, playlist_id, next_page_token=None):
    print("loading playlist next_page_token:", next_page_token)
    url = "https://www.googleapis.com/youtube/v3/playlistItems"

    querystring = {
        "part":"snippet",
        "maxResults":"1",
        "playlistId":playlist_id,
        "key":api_key
        }
    if next_page_token is not None:
        querystring['pageToken'] = next_page_token

    response = requests.request("GET", url, params=querystring)
    json = response.json()
    items = json['items']
    for item in items:
        video_id = item['snippet']['resourceId']['videoId']
        item['transcript'] = load_transcript(video_id)

    results.append(items)
    if 'nextPageToken' in json:
        load_playlist(api_key, playlist_id, json['nextPageToken'])

    return results
def load_transcript(video_id):
    print("download transcript video_id: {}".format(video_id))

    url = "http://video.google.com/timedtext"

    querystring = {
        "lang":"en",
        "v":video_id
    }
    # print("load video",video_id)
    response = requests.request("GET", url, params=querystring)
    if not response.ok:
        print("could not get transcript for {} !200".format(video_id))
        return ''

    try:
        transcript = ''
        tree = ElementTree.fromstring(response.text)
        for elem in tree:
            transcript += elem.text + " "
        return transcript
    except:
        print("could not get transcript for {} xml parse error".format(video_id))
        return ''

def main(api_key=YT_API_KEY, playlist_id=playlist_id):
    json_results = load_playlist(api_key, playlist_id)

    #flatten the list
    flat_list = []
    for sublist in json_results:
        for item in sublist:
            flat_list.append(item)
    #convert to dataframe
    df = json_normalize(flat_list)
    #save the dataframe as csv
    df.to_csv('test.csv')
    print("file saved")

if __name__ == '__main__':
    main(api_key=YT_API_KEY, playlist_id=playlist_id)
