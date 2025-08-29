import asyncio
from typing import AsyncIterator, Dict, List
from selectolax.parser import HTMLParser
from .base import CrawlConfig, Product, BrowserPool, fetch_html, throttle, select_text
from ..utils.robots import is_allowed

LIST_CARD = 'div.cl'  # IndiaMART listing card (may drift)
TITLE_SEL = 'a.lcname'
PRICE_SEL = 'span.prc'  # price span
MIN_ORDER_SEL = 'span.prc + span'  # heuristic
COMPANY_SEL = 'a.cmpny'
LOCATION_SEL = 'span.cty'

async def crawl_indiamart(category_name: str, category_url: str, cfg: CrawlConfig) -> AsyncIterator[Product]:
    if not await is_allowed(category_url):
        return
    async with BrowserPool(cfg) as pool:
        page = await pool.new_page()
        url = category_url
        for page_no in range(1, 1000):
            html = await fetch_html(page, url)
            tree = HTMLParser(html)
            cards = tree.css(LIST_CARD)
            if not cards:
                break
            for c in cards:
                yield Product(
                    site='indiamart',
                    category=category_name,
                    title=select_text(c, TITLE_SEL),
                    price_raw=select_text(c, PRICE_SEL),
                    min_order=select_text(c, MIN_ORDER_SEL),
                    product_url=(c.css_first(TITLE_SEL).attributes.get('href') if c.css_first(TITLE_SEL) else None),
                    company_name=select_text(c, COMPANY_SEL),
                    company_url=(c.css_first(COMPANY_SEL).attributes.get('href') if c.css_first(COMPANY_SEL) else None),
                    location=select_text(c, LOCATION_SEL),
                    description=None
                )
            # Try next page
            next_link = tree.css_first('a[rel="next"], a:contains("Next")')
            if not next_link:
                break
            href = next_link.attributes.get('href')
            if not href:
                break
            if href.startswith('http'):
                url = href
            else:
                from urllib.parse import urljoin
                url = urljoin(url, href)
            await throttle(cfg)
