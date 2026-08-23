import io
import time
import requests
from pathlib import Path
from PIL import Image

url = "https://commons.wikimedia.org/w/api.php"
headers = {"User-Agent": "WeirdImageFinder/0.1 (https://example.org; contact@example.org)"}


def fetch_random_batch(count, on_progress=None):
    """Fetch random Commons photos into memory only (nothing saved to disk).

    Returns a list of (safe_name, image, page_url, thumb_url) tuples so the
    caller can decide what's worth keeping. page_url is the image's Commons page;
    thumb_url is the 320px thumbnail (handy for embedding in a gallery).
    If on_progress is given, it's called with the running download count after
    each successful image so callers can show live progress. Non-photo or failed
    files are skipped silently (keeps a single-line status display tidy).
    """
    params = {
        "action": "query",
        "format": "json",
        "generator": "random",
        "grnnamespace": 6,
        "grnlimit": count,
        "prop": "imageinfo",
        "iiprop": "url|mediatype|mime",
        "iiurlwidth": 320,
    }
    response = requests.get(url, params=params, headers=headers, timeout=30)
    data = response.json()

    results = []
    pages = data["query"]["pages"]
    for page in pages.values():
        title = page["title"]
        try:
            info = page["imageinfo"][0]
            if info["mediatype"] != "BITMAP" or info["mime"] != "image/jpeg":
                continue
            time.sleep(1)
            image_response = requests.get(info["thumburl"], headers=headers, timeout=30)
            image = Image.open(io.BytesIO(image_response.content))
            safe_name = Path(title).stem.replace("File:", "").replace("/", "_")[:100]
            results.append((safe_name, image, info["descriptionurl"], info["thumburl"]))
            if on_progress:
                on_progress(len(results))
        except Exception:
            continue      # skip non-image / failed downloads quietly
    return results
