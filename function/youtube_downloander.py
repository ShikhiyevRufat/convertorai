import yt_dlp as youtube_dl
import os

def youtube_downloader(url, format, resolution=None):
    try:
        video_info = youtube_dl.YoutubeDL().extract_info(url=url, download=False)
        
        safe_title = "".join([c if c.isalnum() or c in (' ', '.', '_') else '' for c in video_info['title']]).rstrip()
        safe_title = safe_title.replace(' ', '_')  
        filename = f"{safe_title}.{format}"
        output_directory = os.path.join(os.getcwd(), "downloads") 
        os.makedirs(output_directory, exist_ok=True)  
        filepath = os.path.join(output_directory, filename)

        options = {
            'outtmpl': filepath,  
            'quiet': False,       
            'merge_output_format': format if format == 'mp4' else None,
            'cookies': 'youtube_cookie.txt',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }

        if format == 'mp3':
            options.update({
                'format': 'bestaudio/best[ext=m4a]',  
                'keepvideo': False,   

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
            })

        with youtube_dl.YoutubeDL(options) as ydl:
            ydl.download([video_info['webpage_url']])

        print(f"Downloaded file path: {filepath}")
        return filepath

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
