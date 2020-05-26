"""
Simple URL Content Cache
I considered using other implementations but found them disappointing.
They all seemed abandoned and not fully featured Django modules.
"""
import os
import time
import requests
import logging


class UrlContentCache:
    """
    Caches URL responses for a configurable duration.

    """
    DURATION = os.getenv('URL_CONTENT_CACHE_DURATION', 1000)
    LOG = logging.getLogger("UrlContentCache")

    def __init__(self):
        # keys are url, values are dictionary of expire time and content
        self.cache = {}

    def fetch(self, url, duration=DURATION):
        content = None

        if self._is_expired(url):
            UrlContentCache.LOG.debug('fetching: %s', url)
            try:
                response = requests.get(url)
                content = response.content
            except requests.ConnectionError:
                UrlContentCache.LOG.debug('failed to fetch: %s', url)
                content = None

        if content is None:
            UrlContentCache.LOG.debug('using cache: %s', url)
            content = self.cache.get(url)['content']

        UrlContentCache.LOG.debug('update cache')
        self._cache_entry(duration, url, content)
        return content

    def _cache_entry(self, duration, url, content):
        UrlContentCache.LOG.debug("caching: %s", str(content)[:30])
        entry = self.cache.get(url)
        UrlContentCache.LOG.debug("new entry: %r", (entry is None))
        entry = self._new_entry(url, content) if not entry else entry
        entry['expire'] = time.time()+duration
        UrlContentCache.LOG.debug("update expire: %r", (entry['expire']))

    def _is_expired(self, url):
        entry = self.cache.get(url)
        expire = entry['expire'] if entry else 1
        now = time.time()
        UrlContentCache.LOG.debug("expired: %r", (now >= expire))
        return now >= expire

    def _new_entry(self, url, content):
        entry = {
            'expire': time.time(),
            'content': content,
        }
        self.cache[url] = entry
        UrlContentCache.LOG.debug("new entry: %s", url)
        return entry
