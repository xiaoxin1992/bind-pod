import logging

from django.core.cache import cache
from rest_framework_simplejwt.settings import api_settings


class CacheBase:
    def __init__(self):
        self.timeout = int(api_settings.ACCESS_TOKEN_LIFETIME.total_seconds())

    def set(self, key, data):
        cache.set(key, data, timeout=self.timeout)

    def get(self, key):
        return cache.get(key)

    def delete(self, key):
        return cache.delete(key)


Cache = CacheBase()
