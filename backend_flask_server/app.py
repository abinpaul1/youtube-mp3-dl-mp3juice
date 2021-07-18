from time import sleep
from flask import Flask, request, send_file, after_this_request, jsonify
import youtube_dl
import os
from random import random

from youtubesearchpython import VideosSearch
from flask_cors import CORS

from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error

import requests

app = Flask(__name__)
CORS(app, resources={"/youtube-dl/search": {"origins": "*"}})

SERVER_HOST =  '0.0.0.0'
SERVER_PORT = 8080

def add_thumbnail(file_path,id, artist=None):
    URL = 'http://img.youtube.com/vi/{}/0.jpg'.format(id)
    print(URL)

    ## Todo: check if binary file is gettable from MP3 object

    audio = MP3(file_path, ID3=ID3)
    idata = requests.get(URL).content

    audio.tags.add(
        APIC(
            encoding=3, # 3 is for utf-8
            mime='image/jpeg', # image/jpeg or image/png
            type=3, # 3 is for the cover image
            data = idata
        )
    )
    audio.save()

@app.route('/youtube-dl/search', methods=['POST'])
def yt_searcher():
    queryToSearch = request.get_json(force=True)['search']
    videosSearch = VideosSearch(queryToSearch, limit = 10)
    result_list = []
    for vid in videosSearch.result()['result']:
        vid_info = {
            'title': vid['title'],
            'id': vid['id'],
            'thumbnail': vid['thumbnails'][0]['url'],
            'duration' : vid['duration'],
            'view_count' : vid['viewCount']['short'],
        }
        result_list.append(vid_info)
    return jsonify(result_list)

@app.route('/youtube-dl/download')
def download_as_audio():
    """
        GET Request with id of video to download
        Returns audio file in mp3 format
    """
    id = request.args.get('ybid')
    print("Got request")

    class MyLogger(object):
        def debug(self, msg):
            pass

        def warning(self, msg):
            pass

        def error(self, msg):
            print(msg)

    def my_hook(d):
        if d['status'] == 'finished':
            print('Downloaded')

    # random number in range of 100 to 200 to prevent multiple downloads
    # 'outmpl' has to be named .m4a, otherwise youtube-dl code postprocessors ffmpef
    #  in def run(self, information), doesnt call ffmpeg4 to convert to mp3
    # File isssue : When outtmpl is named as something.mp3, the audio is not converted because of
    # fear of overwriting
    sample_name = str(int(random()*1000))
    audio_file_path = './downloadedsongs/{}.mp3'.format(sample_name)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'logger': MyLogger(),
        'outtmpl': './downloadedsongs/{}.m4a'.format(sample_name),
        'progress_hooks': [my_hook]
    }

    link = 'https://www.youtube.com/watch?v={}'.format(id)
    ydl = youtube_dl.YoutubeDL(ydl_opts)
    info_dict = ydl.extract_info(link, download=False)
    video_title = info_dict.get('title', None)
    ydl.download([link])

    print("Converted")

    add_thumbnail(audio_file_path, id, info_dict.get('artist', None))

    @after_this_request
    def delete(response):
        ## Delete cached file afer sending back to user
        print("Sent")
        os.remove(os.path.abspath(audio_file_path))
        return response

    return send_file(audio_file_path, as_attachment=True, download_name=video_title+".mp3")

if __name__ == '__main__':
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=True)