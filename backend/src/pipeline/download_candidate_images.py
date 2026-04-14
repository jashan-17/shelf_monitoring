from argparse import ArgumentParser
from pathlib import Path

from icrawler.builtin import BingImageCrawler

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CANDIDATE_ROOT = PROJECT_ROOT / "data" / "collected_candidates"

DEFAULT_QUERIES = {
    "empty": [
        "empty supermarket shelf",
        "grocery shelf empty stock",
        "retail shelf stockout",
    ],
    "low": [
        "low stock supermarket shelf",
        "partially empty grocery shelf",
        "retail shelf low inventory",
    ],
    "medium": [
        "partially stocked supermarket shelf",
        "medium stock grocery shelf",
        "retail shelf moderate inventory",
    ],
    "full": [
        "fully stocked supermarket shelf",
        "grocery shelf full stock",
        "retail aisle fully stocked",
    ],
}


def build_parser():
    parser = ArgumentParser(
        description="Download candidate shelf images into a separate review folder."
    )
    parser.add_argument(
        "--per-query",
        type=int,
        default=40,
        help="Number of images to download for each search query.",
    )
    parser.add_argument(
        "--max-num",
        type=int,
        default=None,
        help="Optional maximum number of images per class after all queries.",
    )
    return parser


def ensure_class_directories():
    CANDIDATE_ROOT.mkdir(parents=True, exist_ok=True)
    for class_name in DEFAULT_QUERIES:
        (CANDIDATE_ROOT / class_name).mkdir(parents=True, exist_ok=True)


def trim_folder(folder_path, max_num):
    if max_num is None:
        return

    image_files = sorted([path for path in folder_path.iterdir() if path.is_file()])
    for extra_file in image_files[max_num:]:
        extra_file.unlink()


def download_for_class(class_name, queries, per_query, max_num):
    output_dir = CANDIDATE_ROOT / class_name

    for query in queries:
        print(f"\nDownloading candidates for '{class_name}' using query: {query}")
        crawler = BingImageCrawler(
            downloader_threads=4,
            storage={"root_dir": str(output_dir)},
        )
        crawler.crawl(
            keyword=query,
            max_num=per_query,
            min_size=(300, 300),
        )

    trim_folder(output_dir, max_num=max_num)
    total_files = len([path for path in output_dir.iterdir() if path.is_file()])
    print(f"Saved {total_files} files in {output_dir}")


def main():
    args = build_parser().parse_args()
    ensure_class_directories()

    print("Candidate image download started.")
    print(f"Output folder: {CANDIDATE_ROOT}")

    for class_name, queries in DEFAULT_QUERIES.items():
        download_for_class(
            class_name=class_name,
            queries=queries,
            per_query=args.per_query,
            max_num=args.max_num,
        )

    print("\nDownload complete.")
    print("Review images manually in data/collected_candidates before moving good files into data/raw_images.")


if __name__ == "__main__":
    main()
