from pathlib import Path
from fetch_images import fetch_random_batch
from clip_score import weird_score

md_path = Path("weird-images.md")
if not md_path.exists():                          # start the gallery file with a table header
    md_path.write_text("# Weird images found\n\n| Score | Preview | Link |\n|------:|---------|------|\n")

threshold = 0.95      # only images CLIP judges > 95% "weird" are worth keeping
checked = 0
saved = 0


def log_to_md(score, safe_name, page_url, thumb_url):
    """Append one row: a clickable thumbnail, the score, and the Commons link.
    Pipes in the name are escaped so they can't break the Markdown table."""
    display = safe_name.replace("|", "\\|")
    row = f"| {score:.3f} | [![]({thumb_url})]({page_url}) | [{display}]({page_url}) |\n"
    with open(md_path, "a") as gallery:
        gallery.write(row)


def status(message):
    """Redraw the current console line in place (no newline) so we don't spam.
    \\r returns to the start of the line; \\033[K clears to the end so a shorter
    message never leaves stray characters behind."""
    print(f"\r\033[K{message}", end="", flush=True)


def announce(message):
    """Print a line that stays on screen, clearing the live status line first."""
    print(f"\r\033[K{message}", flush=True)


announce("Hunting for weird images... (Ctrl-C to stop)")
while True:                                       # run forever, until the script is stopped
    try:
        batch = fetch_random_batch(
            50,
            on_progress=lambda n: status(f"⬇️  Downloading batch — {n} photos" + "." * (n % 4)),
        )
    except Exception as error:
        announce(f"batch failed ({error}), retrying...")
        continue

    for i, (safe_name, image, page_url, thumb_url) in enumerate(batch, start=1):
        checked += 1
        status(f"\U0001f50d Scoring {i}/{len(batch)}  (checked {checked}, saved {saved})" + "." * (i % 4))
        score = weird_score(image)                # Stage 2 (CLIP): weirdness probability, 0-1
        if score > threshold:                     # a keeper — log it and announce it
            log_to_md(score, safe_name, page_url, thumb_url)
            saved += 1
            announce(f"\U0001f300 WEIRD  {score:.3f}  {page_url}")

    status(f"\U0001f634 Batch done — checked {checked}, saved {saved}. Fetching more")
