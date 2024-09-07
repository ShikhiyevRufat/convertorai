def tiktok_downloander():
    import pyktok as pyk
    pyk.specify_browser('chrome')

    url = input("Add tiktok url:")

    print(url)

    pyk.save_tiktok(url,
                True,
                    'video_data.csv',
            'chrome')
