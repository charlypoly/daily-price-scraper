"""Scrape product prices from the URLs in urls.txt and append them to data/prices.csv."""

import csv
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}
OUTPUT = Path("data/prices.csv")
PRICE_RE = re.compile(r"[\d,]+\.\d{2}")


def parse(html: str) -> tuple[str | None, float | None]:
    soup = BeautifulSoup(html, "html.parser")
    title = soup.select_one("h1")
    price_el = soup.select_one("[itemprop=price], .price, [data-price]")
    price = None
    if price_el:
        raw = price_el.get("content") or price_el.get("data-price") or price_el.get_text()
        match = PRICE_RE.search(str(raw))
        if match:
            price = float(match.group().replace(",", ""))
    return (title.get_text(strip=True) if title else None), price


def scrape(url: str) -> dict:
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    name, price = parse(response.text)
    return {"url": url, "name": name, "price": price}


def main() -> int:
    urls = [u.strip() for u in Path("urls.txt").read_text().splitlines() if u.strip()]
    OUTPUT.parent.mkdir(exist_ok=True)
    new_file = not OUTPUT.exists()
    failures = 0
    with OUTPUT.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["scraped_at", "url", "name", "price"])
        if new_file:
            writer.writeheader()
        for url in urls:
            try:
                row = scrape(url)
                writer.writerow({"scraped_at": datetime.now(timezone.utc).isoformat(), **row})
                print(f"OK   {url} -> {row['price']}")
            except requests.RequestException as exc:
                failures += 1
                print(f"FAIL {url}: {exc}", file=sys.stderr)
            time.sleep(1)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
