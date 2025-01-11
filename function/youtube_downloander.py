import yt_dlp
import os
from datetime import datetime
import logging
import csv
import json

config_file = 'config.json'
default_config = {
    "default_format": "show_all", 
    "download_directory": "media",  
    "history_file": "download_history.csv"  
}

def load_config():
    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=4)
    with open(config_file, 'r') as f:
        return json.load(f)

config = load_config()
download_directory = config['download_directory']
history_file = config['history_file']

if not os.path.exists(download_directory):
    os.makedirs(download_directory)

def log_download(url, status, timestamp=None):
    """
    Log the download status in both history and log file.
    """
    if not timestamp:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(history_file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([url, status, timestamp])
    logging.info(f"Download status for {url}: {status}")

def download_youtube_or_tiktok_video(url, format_choice):
    try:
        if format_choice == 'mp3':
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(download_directory, '%(title)s.%(ext)s'),
                'postprocessors': [
                    {
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    },
                    {
                        'key': 'FFmpegMetadata' 
                    }
                ],
                'noplaylist': True, 
            }
        else:
            resolution = format_choice.split('_')[1]
            ydl_opts = {
                'format': f'bestvideo[height<={resolution}]+bestaudio/best',
                'merge_output_format': 'mp4',
                'outtmpl': os.path.join(download_directory, '%(title)s.%(ext)s'),
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filepath = ydl.prepare_filename(info)

            if format_choice == 'mp3':
                mp3_filepath = filepath.replace('.webm', '.mp3')
                if os.path.exists(mp3_filepath):
                    return mp3_filepath

            return filepath
    except Exception as e:
        logging.error(f"Error downloading video: {str(e)}")
        return None
