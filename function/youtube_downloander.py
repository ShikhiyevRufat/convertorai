import yt_dlp as youtube_dl
import os

def youtube_downloader(url, format, resolution=None):
    try:
        # Extract video info without downloading
        video_info = youtube_dl.YoutubeDL().extract_info(url=url, download=False)
        
        # Create a safe filename by removing invalid characters
        safe_title = "".join([c if c.isalnum() or c in (' ', '.', '_') else '' for c in video_info['title']]).rstrip()
        safe_title = safe_title.replace(' ', '_')  # Replace spaces with underscores
        filename = f"{safe_title}.{format}"
        output_directory = os.path.join(os.getcwd(), "downloads")  # Save in a 'downloads' folder
        os.makedirs(output_directory, exist_ok=True)  # Ensure the folder exists
        filepath = os.path.join(output_directory, filename)

        # Set download options
        options = {
            'outtmpl': filepath,  # Specify the output template
            'quiet': False,       # Show download progress
            'merge_output_format': format if format == 'mp4' else None
        }

        if format == 'mp3':
            options.update({
                'format': 'bestaudio/best[ext=m4a]',  # Audio only
                'keepvideo': False,                  # Don't keep video for mp3
            })
        elif format == 'mp4':
            # Adjust video resolution based on input
            format_option = 'bestvideo+bestaudio'
            if resolution == '1080p':
                format_option = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'
            elif resolution == '720p':
                format_option = 'bestvideo[height<=720]+bestaudio/best[height<=720]'
            elif resolution == '360p':
                format_option = 'bestvideo[height<=360]+bestaudio/best[height<=360]'

            options.update({
                'format': format_option,  # Video + audio merge
            })

        # Download the video/audio
        with youtube_dl.YoutubeDL(options) as ydl:
            ydl.download([video_info['webpage_url']])

        print(f"Downloaded file path: {filepath}")
        return filepath

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
