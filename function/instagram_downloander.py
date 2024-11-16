import time
import instaloader
import requests
from io import BytesIO

def instagram_downloander(url, content_type):
    print(f"Content Type: {content_type}")

    try:
        ig = instaloader.Instaloader()

        shortcode = url.split('/')[-2]
        post = instaloader.Post.from_shortcode(ig.context, shortcode)

        if content_type == 'post' or content_type == 'reel':
            if post.is_video:
                video_url = post.video_url
                response = requests.get(video_url)
                if response.status_code == 200:
                    return BytesIO(response.content), 'video'
            else:
                image_url = post.url
                response = requests.get(image_url)
                if response.status_code == 200:
                    return BytesIO(response.content), 'image'

            print("No media found.")
            return None, None

        else:
            print("Invalid content type. Please enter 'post' or 'reel'.")
            return None, None

    except instaloader.exceptions.BadResponseException as e:
        print(f"An error occurred while fetching post metadata: {e}")
        return None, None
    except requests.exceptions.RequestException as e:
        if "401" in str(e) or "429" in str(e):
            print("Rate limit exceeded. Waiting before retrying...")
            time.sleep(60)  
            return instagram_downloander(url, content_type) 
        print(f"Unexpected error: {e}")
        return None, None
