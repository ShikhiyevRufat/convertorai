import time
import instaloader
import requests
from io import BytesIO
import os

INSTAGRAM_USERNAME = "omnitekra"
INSTAGRAM_PASSWORD = "Sirqoc233.Qocsir323"

def instagram_downloander(url, content_type):
    try:
        ig = instaloader.Instaloader()

        # Load session
        session_dir = os.path.join(os.getcwd(), 'insta_sessions')
        os.makedirs(session_dir, exist_ok=True)
        session_file = os.path.join(session_dir, f"session-{INSTAGRAM_USERNAME}")
        try:
            ig.load_session_from_file(INSTAGRAM_USERNAME, session_file)
        except FileNotFoundError:
            ig.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
            ig.save_session_to_file(session_file)

        shortcode = url.split('/')[-2]
        for _ in range(3):  # Retry logic
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
    except Exception as e:
        print(f"Error: {e}")
        return None, None
