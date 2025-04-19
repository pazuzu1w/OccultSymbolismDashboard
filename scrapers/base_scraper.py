# scrapers/base_scraper.py
import requests
from bs4 import BeautifulSoup
import logging
import time
import random
from abc import ABC, abstractmethod
from requests.exceptions import RequestException


class BaseScraper(ABC):
    """Base class for all scrapers with advanced capabilities"""

    def __init__(self, url=None, urls=None, headers=None, proxies=None):
        """
        Initialize with either a single URL or list of URLs

        Args:
            url: Single URL to scrape
            urls: List of URLs to scrape
            headers: Custom headers for requests
            proxies: Proxy configuration for requests
        """
        if url and urls:
            raise ValueError("Provide either url or urls, not both")

        self.url = url
        self.urls = urls or (url and [url]) or []
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }
        self.proxies = proxies
        self.results = []
        self.soup = None
        self.current_url = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.retries = 3
        self.retry_delay = 5
        self.jitter = 2  # Random delay variation

    def fetch(self, url=None):
        """
        Fetch content from URL with retry logic and error handling

        Args:
            url: URL to fetch, defaults to self.url if not provided

        Returns:
            BeautifulSoup object or None if fetch failed
        """
        if url is None:
            url = self.url

        if not url:
            self.logger.error("No URL provided")
            return None

        self.current_url = url

        for attempt in range(self.retries):
            try:
                # Add random delay to avoid being blocked
                if attempt > 0:
                    delay = self.retry_delay + random.uniform(0, self.jitter)
                    self.logger.info(f"Retry {attempt + 1}/{self.retries}, waiting {delay:.2f}s")
                    time.sleep(delay)

                self.logger.info(f"Fetching {url}")
                response = requests.get(
                    url,
                    headers=self.headers,
                    proxies=self.proxies,
                    timeout=30
                )

                response.raise_for_status()

                if not response.content:
                    self.logger.warning(f"Empty response from {url}")
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')
                self.soup = soup

                # Check if we've been blocked or got a captcha page
                if self._is_blocked(soup):
                    self.logger.warning("Detected blocking page or captcha")
                    continue

                return soup

            except RequestException as e:
                self.logger.error(f"Error fetching {url}: {str(e)}")
                if attempt == self.retries - 1:
                    self.logger.error(f"Max retries reached for {url}")
                    return None

        return None

    def fetch_all(self):
        """Fetch all URLs in self.urls"""
        self.results = []

        for url in self.urls:
            soup = self.fetch(url)
            if soup:
                raw_data = self.extract(soup, url)
                if raw_data:
                    transformed_data = self.transform(raw_data, url)
                    if transformed_data:
                        if isinstance(transformed_data, list):
                            self.results.extend(transformed_data)
                        else:
                            self.results.append(transformed_data)

        return self.results

    def _is_blocked(self, soup):
        """
        Check if response indicates we've been blocked or hit a captcha

        Override this in subclasses to add site-specific detection
        """
        # Generic blocking detection
        indicators = [
            # Common captcha indicators
            "captcha", "robot", "automated access", "verify you are a human",
            # Cloudflare indicators
            "attention required", "security check", "ray id",
            # Generic block indicators
            "access denied", "blocked", "too many requests", "rate limited"
        ]

        page_text = soup.get_text().lower()

        for indicator in indicators:
            if indicator in page_text:
                return True

        # Check for very short response which could indicate a redirect to a block page
        if len(page_text) < 100:
            common_elements = soup.find_all(['p', 'div', 'h1', 'h2', 'h3'])
            if len(common_elements) < 3:
                return True

        return False

    @abstractmethod
    def extract(self, soup, url):
        """
        Extract data from the soup object - must be implemented by subclasses

        Args:
            soup: BeautifulSoup object
            url: URL being processed

        Returns:
            Extracted raw data
        """
        pass

    @abstractmethod
    def transform(self, data, url):
        """
        Transform scraped data to match our data model - must be implemented by subclasses

        Args:
            data: Raw extracted data
            url: URL being processed

        Returns:
            Transformed data matching our model
        """
        pass

    def run(self):
        """Execute the full scraping process"""
        if self.url:
            soup = self.fetch()
            if soup:
                raw_data = self.extract(soup, self.url)
                if raw_data:
                    return self.transform(raw_data, self.url)
            return None
        else:
            return self.fetch_all()

    def clean_text(self, text):
        """Clean text by removing extra spaces, newlines, etc."""
        if not text:
            return ""

        # Replace multiple whitespace with single space
        text = ' '.join(text.split())

        # Remove leading/trailing whitespace
        return text.strip()