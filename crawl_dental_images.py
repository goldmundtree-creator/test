#!/usr/bin/env python3
"""
Dental clinical image crawler using icrawler.

Downloads reference dental clinical images from Google/Bing
for dental consultation purposes.

Usage:
    pip install icrawler
    python crawl_dental_images.py

Options (via environment variables or command-line):
    TARGET_COUNT=100        Number of images to download (default: 100)
    SAVE_DIR=./dental_images  Directory to save images (default: ./dental_images)

Notes:
    - Images are sourced from Bing/Google image search
    - Duplicate images are automatically removed after download
    - The script uses multiple dental-related search queries for diversity
    - Respect copyright: downloaded images may be subject to usage restrictions
"""

import argparse
import os
import sys
import time
import hashlib
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

DEFAULT_SAVE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "dental_images"
)
DEFAULT_TARGET_COUNT = 100

# Multiple search queries to get diverse dental clinical images.
# Mixing English and Korean terms for broader coverage.
SEARCH_QUERIES = [
    "dental clinical photography intraoral",
    "dental caries clinical photo",
    "periodontal disease clinical image",
    "dental crown bridge clinical photo",
    "orthodontic treatment progress photo",
    "dental implant clinical image",
    "tooth extraction clinical photo",
    "dental veneer before after clinical",
    "root canal treatment xray clinical",
    "치과 임상사진",
    "치과 교정 임상 사진",
    "치아 우식증 사진",
]

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp")


def count_images(directory):
    """Count image files in a directory."""
    if not os.path.isdir(directory):
        return 0
    return len(
        [f for f in os.listdir(directory) if f.lower().endswith(IMAGE_EXTENSIONS)]
    )


def crawl_with_bing(query, save_dir, max_num):
    """Try crawling with Bing. Returns True if any images were found."""
    from icrawler.builtin import BingImageCrawler

    crawler = BingImageCrawler(
        storage={"root_dir": save_dir},
        downloader_threads=4,
        log_level=logging.WARNING,
    )
    crawler.crawl(
        keyword=query,
        max_num=max_num,
        filters={"type": "photo", "size": "medium"},
    )
    return True


def crawl_with_google(query, save_dir, max_num):
    """Try crawling with Google. Returns True if any images were found."""
    from icrawler.builtin import GoogleImageCrawler

    crawler = GoogleImageCrawler(
        storage={"root_dir": save_dir},
        downloader_threads=4,
        log_level=logging.WARNING,
    )
    crawler.crawl(
        keyword=query,
        max_num=max_num,
        filters={"type": "photo", "size": "medium"},
    )
    return True


def crawl_images(save_dir, target_count):
    """Download dental clinical images using icrawler."""
    try:
        from icrawler.builtin import GoogleImageCrawler, BingImageCrawler  # noqa: F401
    except ImportError:
        logger.error(
            "icrawler is not installed. Install it with:\n"
            "  pip install icrawler"
        )
        sys.exit(1)

    os.makedirs(save_dir, exist_ok=True)
    images_per_query = target_count // len(SEARCH_QUERIES) + 1
    total_downloaded = 0

    for i, query in enumerate(SEARCH_QUERIES):
        if total_downloaded >= target_count:
            break

        remaining = target_count - total_downloaded
        count = min(images_per_query, remaining)

        logger.info(
            f"[{i+1}/{len(SEARCH_QUERIES)}] Searching: '{query}' "
            f"(requesting {count} images)"
        )

        # Try Bing first (more lenient rate limiting), fall back to Google
        try:
            crawl_with_bing(query, save_dir, count)
        except Exception as e:
            logger.warning(f"Bing failed for '{query}': {e}")
            try:
                crawl_with_google(query, save_dir, count)
            except Exception as e2:
                logger.warning(f"Google also failed for '{query}': {e2}")

        current_count = count_images(save_dir)
        newly_downloaded = current_count - total_downloaded
        total_downloaded = current_count
        logger.info(
            f"  -> Downloaded {newly_downloaded} images (total: {total_downloaded})"
        )

        # Rate-limit: small delay between queries
        if i < len(SEARCH_QUERIES) - 1 and total_downloaded < target_count:
            time.sleep(2)

    logger.info(f"Done! Total images downloaded: {total_downloaded}")
    logger.info(f"Saved to: {save_dir}")
    return total_downloaded


def deduplicate_images(save_dir):
    """Remove duplicate images based on file content hash."""
    if not os.path.isdir(save_dir):
        return

    seen_hashes = {}
    removed = 0

    for fname in sorted(os.listdir(save_dir)):
        fpath = os.path.join(save_dir, fname)
        if not os.path.isfile(fpath):
            continue

        with open(fpath, "rb") as f:
            file_hash = hashlib.md5(f.read()).hexdigest()

        if file_hash in seen_hashes:
            os.remove(fpath)
            removed += 1
            logger.info(
                f"Removed duplicate: {fname} (same as {seen_hashes[file_hash]})"
            )
        else:
            seen_hashes[file_hash] = fname

    if removed > 0:
        logger.info(f"Removed {removed} duplicate images")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Download dental clinical reference images from web image search."
    )
    parser.add_argument(
        "-n",
        "--count",
        type=int,
        default=int(os.environ.get("TARGET_COUNT", DEFAULT_TARGET_COUNT)),
        help=f"Number of images to download (default: {DEFAULT_TARGET_COUNT})",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=os.environ.get("SAVE_DIR", DEFAULT_SAVE_DIR),
        help=f"Output directory (default: {DEFAULT_SAVE_DIR})",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    save_dir = args.output
    target_count = args.count

    logger.info(f"Target: {target_count} dental clinical images")
    logger.info(f"Save directory: {save_dir}")
    logger.info(f"Search queries: {len(SEARCH_QUERIES)}")
    print()

    crawl_images(save_dir, target_count)
    deduplicate_images(save_dir)

    final_count = count_images(save_dir)
    logger.info(f"Final image count: {final_count}")

    if final_count < target_count:
        logger.warning(
            f"Only got {final_count}/{target_count} images. "
            "You can re-run the script or add more search queries to SEARCH_QUERIES."
        )


if __name__ == "__main__":
    main()
