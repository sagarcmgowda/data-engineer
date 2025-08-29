import asyncio
from typing import AsyncIterator, Dict, List
from selectolax.parser import HTMLParser
from .base import CrawlConfig, Product, BrowserPool, fetch_html, throttle, select_text
from ..utils.robots import is_allowed

LIST_CARD = 'div.organic-offer-wrapper'  # Alibaba listing card (may drift)
TITLE_SEL = 'h2 a.elements-title-normal__content'
PRICE_SEL = 'div.price span'
MIN_ORDER_SEL = 'div.quantity span'
COMPANY_SEL = 'a.supplier__name'
LOCATION_SEL = 'span.supplier__region'

async def crawl_alibaba(category_name: str, category_url: str, cfg: CrawlConfig) -> AsyncIterator[Product]:
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
                title_el = c.css_first(TITLE_SEL)
                company_el = c.css_first(COMPANY_SEL)
                yield Product(
                    site='alibaba',
                    category=category_name,
                    title=title_el.text(strip=True) if title_el else None,
                    price_raw=select_text(c, PRICE_SEL),
                    min_order=select_text(c, MIN_ORDER_SEL),
                    product_url=(title_el.attributes.get('href') if title_el else None),
                    company_name=company_el.text(strip=True) if company_el else None,
                    company_url=(company_el.attributes.get('href') if company_el else None),
                    location=select_text(c, LOCATION_SEL),
                    description=None
                )
            # Next page
            next_link = tree.css_first('a[aria-label="next"], a.next')
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
