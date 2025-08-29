import asyncio, random, time
from dataclasses import dataclass
from typing import AsyncIterator, Dict, List, Optional
from urllib.parse import urljoin
from pydantic import BaseModel, Field
from playwright.async_api import async_playwright
from selectolax.parser import HTMLParser
from ..utils.robots import is_allowed
from ..utils.text import clean_whitespace

DEFAULT_UA = (
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
)

@dataclass
class CrawlConfig:
    delay: float = 3.0
    jitter: float = 1.0
    headless: bool = True
    concurrency: int = 1
    user_agent: str = DEFAULT_UA

class Product(BaseModel):
    site: str
    category: str
    title: Optional[str] = None
    price_raw: Optional[str] = None
    min_order: Optional[str] = None
    product_url: Optional[str] = None
    company_name: Optional[str] = None
    company_url: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    ts: float = Field(default_factory=lambda: time.time())

async def throttle(cfg: CrawlConfig):
    delay = max(0, random.gauss(cfg.delay, cfg.jitter))
    await asyncio.sleep(delay)

class BrowserPool:
    def __init__(self, cfg: CrawlConfig):
        self.cfg = cfg
        self._browser = None
        self._context = None

    async def __aenter__(self):
        self._pw = await async_playwright().start()
        self._browser = await self._pw.chromium.launch(headless=self.cfg.headless)
        self._context = await self._browser.new_context(user_agent=self.cfg.user_agent)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._context.close()
        await self._browser.close()
        await self._pw.stop()

    async def new_page(self):
        return await self._context.new_page()

async def fetch_html(page, url: str) -> str:
    await page.goto(url, wait_until='domcontentloaded', timeout=60000)
    await asyncio.sleep(1.0)  # give time for lazy content
    return await page.content()

def select_text(node, selector: str) -> Optional[str]:
    el = node.css_first(selector)
    return clean_whitespace(el.text()) if el else None
