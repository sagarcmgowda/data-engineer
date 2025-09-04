# B2B Market Scraper: IndiaMART / Alibaba (Crawler → ETL → EDA)

An end-to-end mini project to crawl product listings from **IndiaMART** and **Alibaba**, normalize and store the data, and run **Exploratory Data Analysis (EDA)** with charts.

>**Important**: Before running the crawler on any website, review and comply with the website's Terms of Service and robots.txt. This code includes a robots.txt pre-check and rate limiting, but *you* are responsible for legal and ethical use.

---

## Quickstart

```bash
# 1) Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2) Install deps
pip install -r requirements.txt

# 3) Install Playwright browser binaries (first time only)
python -m playwright install chromium

# 4) Run a small demo crawl (safe defaults & slow rate limits)
python run_crawl.py --site indiamart --categories config/indiamart_categories.json --max-pages 1 --out data/indiamart_raw.jsonl

# 5) Normalize + export CSV/Parquet
python src/etl/normalize.py --inputs data/indiamart_raw.jsonl --out-csv data/indiamart_clean.csv --out-parquet data/indiamart_clean.parquet

# 6) EDA (creates charts under outputs/figures/ and a summary CSV)
python src/eda/eda.py --input data/indiamart_clean.csv --report outputs/eda_summary.json
```
## Design Notes

- **Playwright (Chromium)** is used for resilient scraping of dynamic pages and to reduce blocks by respecting delays and realistic headers.
- **Rate limiting + jitter** and **robots.txt** checks built-in.
- **Pydantic** schema enforces structured records.
- **JSONL raw dump** → **normalized CSV/Parquet** with cleaned price fields, location splits, and keyword extraction.
- **EDA** produces summary stats + charts: top categories, price distributions, supplier regions, and keyword frequencies.

---

## Legal / Ethical Use

- Only crawl pages permitted by `robots.txt` and ToS.
- Use reasonable `--delay` and `--concurrency 1-2` settings.
- Cache pages locally for experimentation.
- If a site disallows scraping, do not proceed.

---

## Troubleshooting

- If selectors drift (sites change HTML), update the CSS/XPath in `src/crawler/*.py`.
- If you get blocked, increase delay, reduce concurrency, and rotate user agents / proxy as needed.
- When no real data is available, use the synthetic generator built into `eda.py` (`--generate-sample`) to test the pipeline.
