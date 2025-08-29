import argparse, asyncio, json
from src.crawler.base import CrawlConfig, Product
from src.crawler.indiamart import crawl_indiamart
from src.crawler.alibaba import crawl_alibaba
from src.storage.writer import write_jsonl
import json

def load_categories(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

async def run(site: str, categories: dict, max_pages: int, out_path: str, delay: float, headless: bool):
    cfg = CrawlConfig(delay=delay, jitter=delay*0.3, headless=headless, concurrency=1)
    async def site_crawler(cat_name, url):
        if site == 'indiamart':
            async for p in crawl_indiamart(cat_name, url, cfg):
                yield p
        elif site == 'alibaba':
            async for p in crawl_alibaba(cat_name, url, cfg):
                yield p
        else:
            raise ValueError('Unsupported site')

    async def gather():
        for cname, url in categories.items():
            page_count = 0
            async for prod in site_crawler(cname, url):
                yield prod
                page_count += 1
                if page_count >= 5000:
                    break

    items = []
    async for p in gather():
        items.append(p.model_dump())
    write_jsonl(out_path, items)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--site', choices=['indiamart', 'alibaba'], required=True)
    ap.add_argument('--categories', required=True, help='Path to JSON of category_name -> url')
    ap.add_argument('--max-pages', type=int, default=1)
    ap.add_argument('--out', required=True)
    ap.add_argument('--delay', type=float, default=3.0)
    ap.add_argument('--no-headless', action='store_true')
    args = ap.parse_args()

    cats = load_categories(args.categories)
    asyncio.run(run(args.site, cats, args.max_pages, args.out, delay=args.delay, headless=not args.no_headless))
