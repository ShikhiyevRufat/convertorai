from yt_download.main import Auto

def youtube_downloader(query_or_urls, formats, qualities = "320"):
    try:
        auto_instance = Auto(query=query_or_urls, format=formats, quality=qualities)
        return auto_instance  
    except Exception as e:
        print(f"Error in youtube_downloader: {e}")
        return None

