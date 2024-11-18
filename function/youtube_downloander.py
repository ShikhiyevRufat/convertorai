from pytubefix import YouTube
import os

def youtube_downloader(url, format, resolution=None):
    try:
        yt = YouTube(url, use_po_token=True)

        # Generate a safe file title
        safe_title = "".join([c for c in yt.title if c.isalnum() or c in (' ', '.', '_')]).rstrip()
        filename = f"{safe_title}.{format}"
        filepath = os.path.join(os.getcwd(), filename)

        if format == 'mp3':
            # Download audio
            stream = yt.streams.filter(only_audio=True, file_extension='mp4').first()
            if stream:
                stream.download(filename=filename)
            else:
                raise Exception("No audio stream found.")
        elif format == 'mp4':
            # Download video based on resolution
            if resolution:
                stream = yt.streams.filter(res=resolution, file_extension='mp4').first()
            else:
                stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            
            if stream:
                stream.download(filename=filename)
            else:
                raise Exception(f"No video stream found for resolution: {resolution}")

        print(f"Downloaded file path: {filepath}")
        return filepath
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
