import yt_dlp

def download_tiktok(video_url, output_filename, target_resolution='720p'):
    try:
        ydl_opts = {'listformats': True,
                    'timeout': 30,}
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            if not info_dict:
                raise ValueError("Failed to extract video information. Please check the URL.")

            formats = info_dict.get('formats', [])
            if not formats:
                raise ValueError("No available formats for the video. Please check the URL.")
            
            selected_format = None
            for fmt in formats:
                if fmt.get('format_id') and target_resolution in fmt['format_id']:
                    selected_format = fmt['format_id']
                    break

            if not selected_format:
                selected_format = formats[-1]['format_id'] 

        ydl_opts = {
            'format': selected_format,
            'outtmpl': output_filename,
            'timeout': 30,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        print(f"Downloaded TikTok video successfully in {target_resolution}.")
    except Exception as e:
        print(f"Error in download_tiktok: {e}")
        raise
