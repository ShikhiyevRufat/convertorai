import yt_dlp as youtube_dl
import os

def youtube_downloander(url, format, resolution=None):
    try:
        video_info = youtube_dl.YoutubeDL().extract_info(url=url, download=False)
        safe_title = "".join([c for c in video_info['title'] if c.isalnum() or c in (' ', '.', '_')]).rstrip()
        filename = f"{safe_title}.{format}"
        filepath = os.path.join(os.getcwd(), filename)

        options = {
            'outtmpl': filepath,
            'age_limit': 21,
            'verbose': True,
            'cookiefile': 'function/youtube_cookie.txt',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }

        if format == 'mp3':
            options.update({
                'format': 'bestaudio/best[ext=m4a]',
                'keepvideo': False,
                'nocheckcertificate': True,
            })
        elif format == 'mp4':
            format_option = 'bestvideo+bestaudio'
            if resolution == '1080p':
                format_option = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'
            elif resolution == '720p':
                format_option = 'bestvideo[height<=720]+bestaudio/best[height<=720]'
            elif resolution == '360p':
                format_option = 'bestvideo[height<=360]+bestaudio/best[height<=360]'
            
            options.update({
                'format': format_option,
                'merge_output_format': 'mp4',
                'nocheckcertificate': True,
            })

        with youtube_dl.YoutubeDL(options) as ydl:
            ydl.download([video_info['webpage_url']])

        print(f"Downloaded file path: {filepath}")

        return filepath
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
