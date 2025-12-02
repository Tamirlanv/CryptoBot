import time

class CacheTTL:
    
    def __init__(self, ttl=10):
        self.ttl = ttl
        self.cache = {}

    def get(self, key):
        data = self.cache.get(key)
        if not data:
            return None
        value, ts = data
        if time.time() - ts < self.ttl:
            return value
        return None

    def set(self, key, value):
        self.cache[key] = (value, time.time())