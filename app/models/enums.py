from enum import Enum


class FetchMethod(str, Enum):
    """Enum for article fetch methods."""
    RSS = "rss"
    SCRAPING = "scraping"
    API = "api"
    MANUAL = "manual"
