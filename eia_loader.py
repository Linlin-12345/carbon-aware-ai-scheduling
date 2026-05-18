"""
eia_loader.py
-------------
Downloads or loads EIA Form 930 BALANCE data (hourly BA-level electricity).

Usage:
    python src/eia_loader.py --year 2025 --output data/raw/

Data source:
    https://www.eia.gov/electricity/gridmonitor/
"""

import os
import argparse
import requests
from pathlib import Path

# EIA Form 930 bulk CSV download URLs (update if EIA changes structure)
EIA_URLS = {
    2025: [
        "https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_BALANCE_2025_Jan_Jun.csv",
        "https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_BALANCE_2025_Jul_Dec.csv",
    ]
}


def download_eia_data(year: int, output_dir: str) -> list[Path]:
    """
    Download EIA Form 930 BALANCE CSV files for a given year.

    Parameters
    ----------
    year : int
        Year to download (e.g. 2025)
    output_dir : str
        Local directory to save files

    Returns
    -------
    list of Path objects pointing to downloaded files
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    if year not in EIA_URLS:
        raise ValueError(f"No EIA download URLs configured for year {year}. "
                         f"Available: {list(EIA_URLS.keys())}")

    downloaded = []
    for url in EIA_URLS[year]:
        filename = url.split("/")[-1]
        filepath = output_path / filename

        if filepath.exists():
            print(f"[SKIP] {filename} already exists at {filepath}")
            downloaded.append(filepath)
            continue

        print(f"[DOWNLOAD] {filename} ...")
        response = requests.get(url, stream=True, timeout=120)
        response.raise_for_status()

        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"[OK] Saved to {filepath}")
        downloaded.append(filepath)

    return downloaded


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download EIA Form 930 data")
    parser.add_argument("--year", type=int, default=2025, help="Year to download")
    parser.add_argument("--output", type=str, default="data/raw/", help="Output directory")
    args = parser.parse_args()

    files = download_eia_data(args.year, args.output)
    print(f"\nDone. {len(files)} file(s) saved to {args.output}")
