"""
Simple URL Content Cache

"""
import time
import requests
import logging

logging.basicConfig(format='%(levelname)s:\t%(message)s', level=logging.DEBUG)
LOG = logging.getLogger("UrlContentCache")


class UrlContentCache:

    # keys are url, values are dictionary of expire time and content
    cache = {}

    def cache_or_fetch(self, duration, url):
        content = None

        if self.is_expired(url):
            LOG.debug('fetching: %s', url)
            try:
                response = requests.get(url)
                content = response.content
            except requests.ConnectionError:
                LOG.debug('failed to fetch: %s', url)
                content = None

        if content is None:
            LOG.debug('using cache: %s', url)
            content = self.cache.get(url)['content']

        LOG.debug('update cache')
        self.cache_entry(duration, url, content)
        return content

    def cache_entry(self, duration, url, content):
        LOG.debug("caching: %s", str(content)[:30])
        entry = self.cache.get(url)
        LOG.debug("new entry: %r", (entry is None))
        entry = self.new_entry(url, content) if not entry else entry
        entry['expire'] = time.time()+duration
        LOG.debug("update expire: %r", (entry['expire']))

    def is_expired(self, url):
        entry = self.cache.get(url)
        expire = entry['expire'] if entry else 1
        now = time.time()
        LOG.debug("expired: %r", (now >= expire))
        return now >= expire

    def new_entry(self, url, content):
        entry = {
            'expire': time.time(),
            'content': content,
        }
        self.cache[url] = entry
        LOG.debug("new entry: %s", url)
        return entry
