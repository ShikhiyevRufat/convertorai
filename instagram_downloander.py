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



# def instagram_downloander():
#     import instaloader
#     import os
#     import time

#     ig = instaloader.Instaloader()

#     def download_instagram_media(url, content_type):
#         shortcode = url.split('/')[-2]
#         download_path = "downloads"
#         os.makedirs(download_path, exist_ok=True)

#         try:
#             if content_type in ['post', 'reel']:
#                 post = instaloader.Post.from_shortcode(ig.context, shortcode)
#                 ig.download_post(post, target=download_path)

#                 files = [f for f in os.listdir(download_path) if f.startswith(shortcode) and (f.endswith('.jpg') or f.endswith('.mp4'))]
#                 print("Files found:", files) 

#                 if not files:
#                     print("Failed to find the downloaded file.")
#                     return

#                 for file in files:
#                     file_path = os.path.join(download_path, file)
#                     print(f"File path: {file_path}") 
#                     if not os.path.exists(file_path):
#                         print("Failed to find the downloaded file.")
#             else:
#                 print("Invalid content type. Please enter 'post' or 'reel'.")
#         except instaloader.exceptions.BadResponseException as e:
#             print(f"An error occurred while fetching post/reel metadata: {e}")
#         except Exception as e:
#             print(f"An unexpected error occurred: {e}")

#     if __name__ == "__main__":
#         while True:
#             try:
#                 content_type = input("Enter the content type ('post' or 'reel'): ").strip().lower()
#                 url = input("Enter the Instagram post/reel URL: ").strip()

#                 if content_type in ['post', 'reel']:
#                     download_instagram_media(url, content_type)
#                 else:
#                     print("Invalid content type. Please enter 'post' or 'reel'.")
                
#             except Exception as e:
#                 print(f"An error occurred: {e}")
#                 time.sleep(1)