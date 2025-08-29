import asyncio, re
from urllib.parse import urlparse
import httpx

async def is_allowed(url: str, user_agent: str = 'Mozilla/5.0') -> bool:
    """Very lightweight robots.txt check. Returns True if allowed, False if disallowed.
    If robots cannot be fetched, defaults to True but you can change this behavior.
    """
    try:
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(robots_url)
            if r.status_code != 200:
                return True
            rules = r.text.splitlines()
            disallows = []
            ua_block = False
            for line in rules:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if line.lower().startswith('user-agent:'):
                    agent = line.split(':', 1)[1].strip()
                    ua_block = agent == '*'  # naive: respect default rules
                elif ua_block and line.lower().startswith('disallow:'):
                    path = line.split(':', 1)[1].strip()
                    disallows.append(path)
            path = parsed.path or '/'
            for d in disallows:
                if d == '':
                    continue
                if path.startswith(d):
                    return False
            return True
    except Exception:
        return True
