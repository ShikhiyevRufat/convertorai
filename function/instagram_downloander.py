import requests
from io import BytesIO

def instagram_downloader(url, content_type):
    print(f"Content Type: {content_type}")
    
    try:
        # Extract the shortcode from the URL
        changing_url = url.split("/")
        url_code = changing_url[4]  # Get the post/reel shortcode
        
        # Request the Instagram GraphQL endpoint
        api_url = f"https://instagram.com/p/{url_code}?__a=1"
        response = requests.get(api_url)
        
        if response.status_code != 200:
            print("Failed to fetch data from Instagram")
            return None, None
        
        post_data = response.json()
        
        # Check if the post is a video or image
        is_video = post_data['graphql']['shortcode_media']['is_video']
        
        if content_type == 'post' or content_type == 'reel':
            if is_video:
                video_url = post_data['graphql']['shortcode_media']['video_url']
                video_response = requests.get(video_url)
                if video_response.status_code == 200:
                    return BytesIO(video_response.content), 'video'
            else:
                image_url = post_data['graphql']['shortcode_media']['display_url']
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    return BytesIO(image_response.content), 'image'
        
        print("No media found.")
        return None, None
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None
