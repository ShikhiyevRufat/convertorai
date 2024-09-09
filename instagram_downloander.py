def instagram_downloander(url, content_type):
    import instaloader
    import os

    ig = instaloader.Instaloader()
    shortcode = url.split('/')[-2]
    download_path = "downloads"
    os.makedirs(download_path, exist_ok=True)

    try:
        if content_type in ['post', 'reel']:
            post = instaloader.Post.from_shortcode(ig.context, shortcode)
            ig.download_post(post, target=download_path)

            files = [f for f in os.listdir(download_path) if f.startswith(shortcode) and (f.endswith('.jpg') or f.endswith('.mp4'))]
            
            if not files:
                print("Failed to find the downloaded file.")
                return None

            # Return the first file (image or video)
            return os.path.join(download_path, files[0])
        else:
            print("Invalid content type. Please enter 'post' or 'reel'.")
            return None
    except instaloader.exceptions.BadResponseException as e:
        print(f"An error occurred while fetching post/reel metadata: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

