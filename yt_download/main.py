import re
import time
import shutil
import logging
import datetime
import typing as t
from tqdm import tqdm
from functools import lru_cache
from pathlib import Path
from os import getcwd, path, environ
from cloudscraper import create_scraper
from requests import Response
import ytube_api.constants as const
import ytube_api.models as models
import ytube_api.exceptions as exception

try:
    import click

    cli_deps_installed = True
except ImportError:
    cli_deps_installed = False

session = create_scraper()

session.headers = const.request_headers


class Ytube:
    def __init__(self, timeout: int = 20, spinner_index: t.Literal[0, 1, 2, 3] = 2):
        self.request_timeout = timeout
        # fix captured so as it match even \W
        self.video_id_patterns = (
            r"^https://youtu.be/([\w+\W*]{11}).*",
            r"^https://www.youtube.com/watch\?v=([\w+\W*]{11}).*",
            r"^https://youtube.com/shorts/([\w+\W*]{11}).*",
            r"^(\w{11})$",
        )
        __spinner = (
            (),
            ("", "-", "\\", "|", "/"),
            (
                "",
                "█■■■■",
                "■█■■■",
                "■■█■■",
                "■■■█■",
                "■■■■█",
            ),
            ("", "⣾ ", "⣽ ", "⣻ ", "⢿ ", "⡿ ", "⣟ ", "⣯ ", "⣷ "),
        )
        if spinner_index < 0 or spinner_index > 3:
            raise ValueError(f"spinner_index must be >=0 or <=3 not {spinner_index}")
        self._spinner_items = __spinner[spinner_index]

    def get(self, *args, **kwargs) -> Response:
        kwargs.setdefault("timeout", self.request_timeout)
        resp = session.get(*args, **kwargs)
        resp.raise_for_status()
        return resp

    def post(self, *args, **kwargs) -> Response:
        kwargs.setdefault("timeout", self.request_timeout)
        resp = session.post(*args, **kwargs)
        resp.raise_for_status()
        return resp

    def get_thumbnail(self, item: models.SearchResultsItem) -> bytes:
        if not isinstance(item, models.SearchResultsItem):
            raise ValueError(
                f"Item should be an instance of {models.SearchResultsItem} "
                f"not {type(item)}"
            )
        return self.get(const.video_thumbnail_url % dict(video_id=item.id)).content
    
    @lru_cache()
    def suggest_queries(self, query: str) -> list[str]:
        """Suggest search queries"""
        text = self.get(const.suggest_queries_url % dict(query=query)).text
        pattern = r'"([^"]+)",0'
        return re.findall(
            pattern,
            text,
        )

    def extract_video_id(self, query: str) -> t.Union[None, str]:
        for pattern in self.video_id_patterns:
            if re.match(pattern, query):
                return re.findall(pattern, query)[0]

    def search_videos(self, query: str) -> models.SearchResults:
        assert query, "Query cannot be empty"
        video_id_from_query = self.extract_video_id(query)
        if video_id_from_query:
            return models.SearchResults(
                query=query,
                items=[
                    models.SearchResultsItem(
                        title=None,
                        id=video_id_from_query,
                        size=None,
                        duration=None,
                        channelTitle=None,
                        source=None,
                    )
                ],
                from_link=True,
            )
        resp = self.get(const.search_videos_url, params=dict(q=query))
        resp.raise_for_status()
        results = resp.json()
        results_items: list[models.SearchResultsItem] = []
        for item in results["items"]:
            results_items.append(models.SearchResultsItem(**item))
        search_results = models.SearchResults(
            query=re.sub(r"\+", " ", results["query"]), items=results_items
        )
        if not search_results.items:
            raise exception.ZeroSearchResults(
                f"Your query '{query}' matched zero videos"
            )
        return search_results

    def get_download_link(
        self,
        item: models.SearchResultsItem,
        format: t.Literal["mp3", "mp4"] = "mp4",
        quality: t.Literal[
            "128", "320", "144", "240", "360", "480", "720", "1080"
        ] = "128|720",
    ) -> models.DownloadLink:
        assert isinstance(item, models.SearchResultsItem), (
            f"Item must be an instance of {models.SearchResultsItem} "
            f"not {type(item)}"
        )
        assert (
            format in const.download_formats
        ), f"Format '{format}' is not one of {[const.audio_download_format, const.video_download_format],}"
        if quality == "128|720":
            if format == const.audio_download_format:
                quality = const.default_audio_download_quality
            else:
                quality = const.default_video_download_quality
        else:
            assert (
                quality in const.download_qualities
            ), f"Quality '{quality}' is not one of {const.download_qualities}"
            if format == const.audio_download_format:
                assert (
                    quality in const.audio_download_qualities
                ), f"Audio quality '{quality}' is not one of {const.audio_download_qualities}"
            if format == const.video_download_format:
                assert (
                    quality in const.video_download_qualities
                ), f"Video quality '{quality}' is not one of {const.video_download_qualities}"
        payload = dict(videoid=item.id, downtype=format, vquality=quality)
        resp_data = self.post(const.to_download_links_url, data=payload).json()
        if resp_data.get("status", "") == "error":
            raise exception.VideoProccessingError(
                str(
                    resp_data.get(
                        "error",
                        "Unknown error occurred while processing video for download.",
                    )
                )
            )
        return models.DownloadLink(**resp_data)

    def download(
        self,
        download_link: models.DownloadLink,
        filename: t.Union[str, Path] = None,
        dir: str = getcwd(),
        progress_bar=True,
        quiet: bool = False,
        progress_callback=None,
        chunk_size: int = 512,
        resume: bool = False,
        leave: bool = True,
        colour: str = "green",
        simple: bool = False,
        experiment: bool = False,
        q: str = " "
    ):
        if resume and not experiment:
            raise Exception(
                f"Cannot resume incomplete downloads in the moment. "
                "However, you can bypass this by activating experimental features by "
                "using --experiment flag in CLI or parameter experiment=True"
            )
        assert isinstance(download_link, models.DownloadLink), (
            f"download_link must be an instance of {models.DownloadLink} "
            f"not {type(download_link)}"
        )
        current_downloaded_size = 0
        current_downloaded_size_in_mb = 0
        filename = filename or download_link.filename
        save_to = Path(dir) / filename
        media_file_url = download_link.url

        def pop_range_in_session_headers():
            if session.headers.get("Range"):
                session.headers.pop("Range")

        def get_busy_bar(prev):
            if not self._spinner_items:
                return ""
            index_of_prev = self._spinner_items.index(prev)
            if index_of_prev == len(self._spinner_items) - 1:
                return self._spinner_items[1]
            else:
                return self._spinner_items[index_of_prev + 1]

        if resume:
            assert path.exists(save_to), f"File not found in path - '{save_to}'"
            current_downloaded_size = path.getsize(save_to)
            # Set the headers to resume download from the last byte
            session.headers.update({"Range": f"bytes={current_downloaded_size}-"})
            current_downloaded_size_in_mb = current_downloaded_size / 1_000_000

        default_content_length = 0
        session.headers["referer"] = const.request_referer
        resp = session.get(media_file_url, stream=True)
        session.headers.pop("referer")
        if not resp.headers.get("content-disposition"):
            raise exception.MediaDownloadError(
                "Server returned unknown response while expecting a media content - "
                f"({resp.status_code}, {resp.reason}) - {resp.text}"
            )

        size_in_bytes = int(resp.headers.get("content-length", default_content_length))
        if not size_in_bytes:
            pass

        if resume:
            assert (
                size_in_bytes != current_downloaded_size
            ), f"Download completed for the file in path - '{save_to}'"

        size_in_mb = (size_in_bytes / 1_000_000) + current_downloaded_size_in_mb
        chunk_size_in_bytes = chunk_size * 1_000

        saving_mode = "ab" if resume else "wb"
        if progress_bar:
            if not quiet:
                print(f"{filename}")
            if (
                not experiment
            ):  # Just a hack to ensure tqdm doesn't handle this by default

                def find_range(start, end, hms: bool = False):
                    in_seconds = round(end - start, 1)
                    return (
                        str(datetime.timedelta(seconds=in_seconds))
                        .split(".")[0]
                        .zfill(8)
                        if hms
                        else in_seconds
                    )

                def get_screen_width():
                    try:
                        return shutil.get_terminal_size().columns
                    except AttributeError:
                        # Fallback for older Python versions
                        return int(environ.get("COLUMNS", 80))
                    
                total_size = int(session.head(media_file_url).headers.get('content-length', 0))
                downloaded_size_in_bytes = current_downloaded_size
                start_time = time.time()
                busy_bar = "" if not self._spinner_items else self._spinner_items[0]
                with open(save_to, saving_mode) as fh:
                    for chunks in resp.iter_content(chunk_size=chunk_size_in_bytes):
                        fh.write(chunks)
                        downloaded_size_in_bytes += len(chunks)
                        if progress_callback:
                            progress_callback(downloaded_size_in_bytes, total_size)
                        text_to_display = f"> Downloaded {round(downloaded_size_in_bytes / 1_000_000, 2)} MB "
                        len_of_more_text_to_display = (
                            get_screen_width()
                            - len(text_to_display)
                            - len(busy_bar)
                            - 24
                        )
                        message_bot =  f"{text_to_display}{'#'*len_of_more_text_to_display} ~ Elapsed ({find_range(start_time, time.time(),True)}) [{busy_bar}]"
                        print(f"{text_to_display}{'#'*len_of_more_text_to_display} ~ Elapsed ({find_range(start_time, time.time(),True)}) [{busy_bar}]", end="\r")
                        busy_bar = get_busy_bar(busy_bar)

                print(
                    "",
                    f"> Download completed successfully ({round(downloaded_size_in_bytes/ 1_000_000, 2)}MB, {find_range(start_time, time.time(), True)})",
                    sep="\n",
                )
                return save_to

            with tqdm(
                desc="Downloading",
                total=round(size_in_mb, 1),
                bar_format=(
                    "{l_bar}{bar} | %(size)s MB" % (dict(size=round(size_in_mb, 1)))
                    if simple
                    else "{l_bar}{bar}{r_bar}"
                ),
                initial=current_downloaded_size_in_mb,
                unit="Mb",
                colour=colour,
                leave=leave,
            ) as p_bar:
                with open(save_to, saving_mode) as fh:
                    for chunks in resp.iter_content(chunk_size=chunk_size_in_bytes):
                        fh.write(chunks)
                        p_bar.update(round(chunk_size_in_bytes / 1_000_000, 1))
                pop_range_in_session_headers()
                return save_to
        else:
            with open(save_to, saving_mode) as fh:
                for chunks in resp.iter_content(chunk_size=chunk_size_in_bytes):
                    fh.write(chunks)

            logging.info(f"{filename} - {size_in_mb}MB ✅")
            pop_range_in_session_headers()
            return save_to
        

def Auto(
    query: str,
    format: t.Literal["mp3", "mp4"] = "mp4",
    quality: t.Literal[
        "128", "320", "144", "240", "360", "480", "720", "1080"
    ] = "128|720",
    limit: int = 1,
    confirm: bool = False,
    timeout: int = 20,
    spinner_index: t.Literal[0, 1, 2, 3] = 2,
    channels: t.Union[list[str], tuple[str]] = [],
    **kwargs,
) -> t.Union[Path, list[Path]]:
    if kwargs.get("filename") and limit > 1:
        raise RuntimeError(
            f"Limit should be 1 when you have specified filename of the item to be downloaded."
        )
    yt = Ytube(timeout=timeout, spinner_index=spinner_index)
    y = yt.search_videos(query)
    saved_to: list[Path] = []
    for count, item in enumerate(y.items, start=1):
        if channels and item.channelTitle not in channels:
            continue
        if confirm and not y.from_link:
            if not cli_deps_installed:
                raise Exception(
                    f"Looks like cli dependencies are not installed. "
                    f"Reinstall ytube-api along with cli extras ie. "
                    "pip install ytube-api[cli]"
                )
            if not click.confirm(
                f'> [{count}/{len(y.items)}] Are you sure to download "{item.title}" by "{item.channelTitle}" ({item.duration})'
            ):
                continue
        d = yt.get_download_link(item, format=format, quality=quality)
        saved = yt.download(d, **kwargs)
        saved_to.append(saved)
        if count >= limit:
            break
    return saved_to[0] if len(saved_to) == 1 else saved_to
