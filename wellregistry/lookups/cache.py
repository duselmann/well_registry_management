"""
Simple URL Content Cache

"""
import time
import requests


class UrlContentCache:

    # keys are url, values are dictionary of expire time and content
    cache = {}

    def cache_or_fetch(self, duration, url):
        if self.is_expired(url):
            print('fetching: ' + url)
            try:
                response = requests.get(url)
                content = response.content
            except requests.ConnectionError:
                print('failed to fetch: ' + url)
                content = None

        if content is None:
            print('using cache: ' + url)
            content = self.cache.get(url)['content']

        print('update cache:')
        self.cache_entry(duration, url, content)
        return content

    def cache_entry(self, duration, url, content):
        print("caching: " + str(content)[:30])
        entry = self.cache.get(url)
        print("new entry: " + str(entry is None))
        entry = self.new_entry(url, content) if not entry else entry
        entry['expire'] = time.time()+duration
        print("update expire: " + str(entry['expire']))

    def is_expired(self, url):
        entry = self.cache.get(url)
        expire = entry['expire'] if entry else 1
        now = time.time()
        print("expired: " + str(now >= expire))
        return now >= expire

    def new_entry(self, url, content):
        entry = {
            'expire': time.time(),
            'content': content,
        }
        self.cache[url] = entry
        print("new entry: " + url)
        return entry
