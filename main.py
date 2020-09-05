from pytube import YouTube
import os
import sys
import glob
import shutil
from moviepy.editor import *
from pydub import AudioSegment


AudioSegment.converter = r"C:\\Users\\Luiz\\AppData\\Local\\Programs\\Python\\Python38\\lib\\site-packages\\pydub\\ffmpeg.exe"

def read_video_urls():
    video_list_file = sys.argv[1]
    with open(video_list_file, "r") as f:
        video_urls = f.read()
    return video_urls.split("\n")


def download_video(url):
    print(url)
    video = YouTube(url)
    video.streams.filter(progressive=True, subtype='mp4').order_by('resolution').desc().last().download()


def gather_video_files():
    video_files = []
    for file in glob.glob("*.mp4"):
        video_files.append(file)
    return video_files


def read_timelist_info(time_list_file):
    song_times = []
    song_names = []
    with open(time_list_file, "r") as f:
        timelist_info = f.read()
    timelist_info = timelist_info.split("\n")
    for song in timelist_info:
        song_times.append(song.split(" ")[0])
        song_names.append(" ".join(song.split(" ")[1:]))
    return song_times, song_names


def split_gig_into_songs(mp3_title, song, song_times, song_names):
    root_dir = os.getcwd()
    gig_dir = mp3_title.replace(".mp3","")
    os.mkdir(gig_dir)
    os.chdir(gig_dir)
    song_times = convert_song_times_to_milliseconds(song_times)
    intro = song[:song_times[0]]
    intro.export("00_intro.mp3", format="mp3")
    for index, name in enumerate(song_names[:-1]):
        current_song = song[song_times[index]:song_times[index+1]]
        clean_name = ''.join(e for e in name if e.isalnum() or e in "_")
        current_song.export(str(index+1).zfill(2) + "_" + clean_name.replace(" ","_") + ".mp3", format="mp3")
    last_song = song[song_times[-1]:]
    last_song.export(str(index+2).zfill(2) + "_" + song_names[-1].replace(" ","_") + ".mp3", format="mp3")
    os.chdir(root_dir)


def convert_song_times_to_milliseconds(song_times):
    new_song_times = []
    for time in song_times:
        seconds_in_ms = int(time.split(":")[-1]) * 1000
        minutes_in_ms = int(time.split(":")[-2]) * 60 * 1000
        try:
            hours_in_ms = int(time.split(":")[-3]) * 60 * 60* 1000
        except:
            hours_in_ms = 0
        new_song_times.append(seconds_in_ms + minutes_in_ms + hours_in_ms)
    return new_song_times


if __name__ == "__main__":
    #video_urls = read_video_urls()
    #for url in video_urls: download_video(url)
    video_files = gather_video_files()
    for video in video_files:
        mp3_title = video.split("\\")[-1].replace("mp4","mp3").replace(" ","_")
        time_list_file = video.split("\\")[-1].replace("mp4","txt")
        song_times, song_names = read_timelist_info(time_list_file)
        videoclip = VideoFileClip(video)
        audioclip = videoclip.audio
        #audioclip.write_audiofile(mp3_title)
        gig = AudioSegment.from_mp3(mp3_title)
        split_gig_into_songs(mp3_title, gig, song_times, song_names)
