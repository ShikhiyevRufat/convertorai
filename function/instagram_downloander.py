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

        for _ in range(3):  
            try:
                post = instaloader.Post.from_shortcode(ig.context, shortcode)
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
            except instaloader.exceptions.TooManyRequestsException:
                print("Rate limit reached. Retrying after delay...")
                time.sleep(600) 
            except Exception as e:
                print(f"Retry failed: {e}")
        print("Unable to download the post. Please try later.")
        return None, None

    except instaloader.exceptions.BadResponseException as e:
        print(f"An error occurred while fetching post metadata: {e}")
        return None, None
    except Exception as e:
        print(f"Unexpected error: {e}")
        time.sleep(10)  
        return instagram_downloander(url, content_type) 
