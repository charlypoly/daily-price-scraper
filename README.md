# daily-price-scraper

Tracks prices for the product pages listed in `urls.txt` and appends them to
`data/prices.csv`. Runs every morning via GitHub Actions
(`.github/workflows/scrape.yml`).

```bash
pip install -r requirements.txt
python scraper.py
```

## Status

Since mid-October most runs fail: requests come back as `403 Forbidden` or a
CAPTCHA page instead of the product page.
