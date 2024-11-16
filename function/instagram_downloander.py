import time
import instaloader
import requests
from io import BytesIO

def instagram_downloader(url):
    """
    Downloads an Instagram post's content (image or video) based on the URL.
    
    Args:
        url (str): The URL of the Instagram post.
    
    Returns:
        tuple: A tuple containing the file content as BytesIO and a string ('image' or 'video').
    """
    print(f"Attempting to download content from URL: {url}")

    # Initialize Instaloader
    ig = instaloader.Instaloader()

    try:
        # Extract shortcode from URL
        shortcode = url.strip('/').split('/')[-1]
        print(f"Extracted shortcode: {shortcode}")

        for attempt in range(3):  # Retry up to 3 times
            try:
                # Fetch post metadata
                post = instaloader.Post.from_shortcode(ig.context, shortcode)

                if post.is_video:
                    video_url = post.video_url
                    print(f"Video URL: {video_url}")
                    response = requests.get(video_url, stream=True)
                    if response.status_code == 200:
                        return BytesIO(response.content), 'video'
                    else:
                        print(f"Failed to download video (HTTP {response.status_code})")

                else:
                    image_url = post.url
                    print(f"Image URL: {image_url}")
                    response = requests.get(image_url, stream=True)
                    if response.status_code == 200:
                        return BytesIO(response.content), 'image'
                    else:
                        print(f"Failed to download image (HTTP {response.status_code})")

            except instaloader.exceptions.TooManyRequestsException:
                print(f"Rate limit reached on attempt {attempt + 1}. Retrying after delay...")
                time.sleep(10 * (attempt + 1))  # Exponential backoff

            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(5)

        print("All retry attempts failed. Please try again later.")
        return None, None

    except instaloader.exceptions.BadResponseException as e:
        print(f"Failed to fetch post metadata: {e}")
        return None, None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None, None
