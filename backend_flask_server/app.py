from time import sleep
from flask import Flask, request, send_file, jsonify
import youtube_dl
from random import random

from youtubesearchpython import VideosSearch
from flask_cors import CORS
from flask_caching import Cache


from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error

import requests

app = Flask(__name__)
CORS(app, resources={r'/youtube-dl/*': {"origins": "*"}})

SERVER_HOST =  '0.0.0.0'
SERVER_PORT = 8080

# TODO : Improve cacheing using redis / memcached
# Uses id of video as key to store details needed to serve file
video_cache_config = {
    "CACHE_TYPE": "FileSystemCache",  # Flask-Caching related configs
    "CACHE_DIR": "./cache/vid_cache_tmp",
    "CACHE_DEFAULT_TIMEOUT": 24*60*60 # Cache cleared every 24 hours
}

processing_queue_cache_config = {
    "CACHE_TYPE": "FileSystemCache",  # Flask-Caching related configs
    "CACHE_DIR": "./cache/proc_q_cache_tmp",
    "CACHE_DEFAULT_TIMEOUT": 60*60 # Cache cleared every hour
}

video_cache = Cache(config=video_cache_config)
processing_queue_cache = Cache(config=processing_queue_cache_config)

video_cache.init_app(app)
processing_queue_cache.init_app(app)

def add_thumbnail(file_path,id, artist=None):
    """
        Utility function to add thumbnail to mp3 file
    """
    URL = 'http://img.youtube.com/vi/{}/0.jpg'.format(id)
    print(URL)

    ## TODO: Add artist metadata to file

    audio = MP3(file_path, ID3=ID3)
    idata = requests.get(URL).content

    ## TODO : Error handling for mutagen
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
    """
        Function to search youtube based on user query and 
        get first 10 result
        Returns a list of json objects with video id, title, 
        thumbnail, duration, view count
    """
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
def download_audio():
    """
        GET Request with id of video to download the converted audio file
        Returns audio file in mp3 format if file is present in cache
    """
    id = request.args.get('ybid')
    print("Got request to download")

    if not video_cache.get(id):
        print("File not found in cache")
        return jsonify(error="Audio file not found. Please convert again"),404

    # Send back file if present in video cache
    print("Found file in cache")
    audio_file_path,video_title = video_cache.get(id)
    print([id,audio_file_path,video_title])
    return send_file(audio_file_path, as_attachment=True, download_name=video_title+".mp3")
        

@app.route('/youtube-dl/convert', methods=['POST'])
def convert_to_audio():
    """
        POST Request to trigger conversion of required video
        to audio file(mp3)
        Returns success on successfull completion
    """
    id = request.get_json(force=True)['ybid']
    print("Got request to convert")


    # Handling possible race condition when a first request to convert 
    # the given video is already being processed
    while(processing_queue_cache.get(id)):
        # wait till it is removed from queue
        # 2 cases : 
        #   failed in first request - retry
        #   success - can be served from cache
        sleep(5)

    processing_queue_cache.set(id, True)

    # If already converted audio is present, return success
    if video_cache.get(id):
        print("File already converted")
        processing_queue_cache.delete(id)
        return jsonify(success="File already converted"),200


    class MyLogger(object):
        def debug(self, msg):
            pass

        def warning(self, msg):
            pass

        def error(self, msg):
            print(msg)

    def my_hook(d):
        if d['status'] == 'finished':
            print('Downloaded audio')

    # 'outmpl' has to be named .m4a, otherwise youtube-dl code postprocessors ffmpef
    #  in def run(self, information), doesnt call ffmpeg4 to convert to mp3
    # File isssue : When outtmpl is named as something.mp3, the audio is not converted because of
    # fear of overwriting

    # random 5 digit number to prevent multiple downloads overwriting each other
    sample_name = str(int(random()*10000))
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

    ## TODO : Error handling for youtube-dl
    info_dict = ydl.extract_info(link, download=False)
    video_title = info_dict.get('title', None)
    ydl.download([link])

    print("Converted to mp3")

    add_thumbnail(audio_file_path, id, info_dict.get('artist', None))

    print("Thumbnail added to mp3")

    video_cache.set(id,[audio_file_path,video_title])
    ## Remove from processing queue once done
    processing_queue_cache.delete(id)

    return jsonify(success="File successfully converted")

if __name__ == '__main__':
    app.run(host=SERVER_HOST, port=SERVER_PORT, threaded=True)