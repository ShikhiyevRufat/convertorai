from ytube_api import Auto

def youtube_downloader(query_or_urls, formats):
    try:
        auto_instance = Auto(query=query_or_urls, format=formats)
        return auto_instance  
    except Exception as e:
        print(f"Error in youtube_downloader: {e}")
        return None
