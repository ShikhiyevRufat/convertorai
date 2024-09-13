import yt_dlp
def download_tiktok(video_url, output_filename, target_resolution='720p'):
    ydl_opts = {
        'listformats': True 
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        formats = info_dict.get('formats', [])

        selected_format = None
        for fmt in formats:
            if target_resolution in fmt['format_id']:
                selected_format = fmt['format_id']
                break

        if not selected_format:
            selected_format = formats[-1]['format_id']

    ydl_opts = {
        'format': selected_format,
        'outtmpl': output_filename  
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        print(f"Downloaded TikTok video successfully in {target_resolution}.")
    except Exception as e:
        print(f"Error downloading video: {e}")

output_filename = 'tiktok_video.mp4'

