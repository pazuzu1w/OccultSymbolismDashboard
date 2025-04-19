# scrapers/search_scraper.py
from .base_scraper import BaseScraper
import re


class SearchScraper(BaseScraper):
    """Scraper for extracting URLs from search engine results"""

    def extract(self, soup, url):
        """Extract search results from the page"""
        self.logger.info(f"Extracting search results from {url}")

        if not soup:
            return None

        results = []

        try:
            # Different extraction based on search engine
            if 'google.com' in url:
                results = self._extract_from_google(soup, url)
            elif 'bing.com' in url:
                results = self._extract_from_bing(soup, url)
            elif 'duckduckgo.com' in url:
                results = self._extract_from_ddg(soup, url)
            else:
                # Generic extraction
                results = self._extract_generic(soup, url)

            self.logger.info(f"Extracted {len(results)} search results from {url}")
            return results

        except Exception as e:
            self.logger.error(f"Error extracting from {url}: {str(e)}")
            return []

    def _extract_from_google(self, soup, url):
        """Extract results from Google search"""
        results = []

        # Try to find search result elements
        search_results = soup.select('.g, .xpd, .res, .search-result')

        if not search_results:
            # Try alternate selectors for Google's changing design
            search_results = soup.select('div[data-hveid]')

        for result in search_results:
            title_elem = result.select_one('h3')
            link_elem = result.select_one('a')

            # Skip if we don't have both
            if not title_elem or not link_elem:
                continue

            title = self.clean_text(title_elem.text)
            link_url = link_elem.get('href', '')

            # Clean up URL if needed
            if link_url.startswith('/url?'):
                # Extract actual URL from Google's redirect
                match = re.search(r'[?&]q=([^&]+)', link_url)
                if match:
                    link_url = match.group(1)

            # Skip unwanted URLs
            if not link_url or link_url.startswith(('/search', '#', 'javascript:')):
                continue

            # Extract description
            desc_elem = result.select_one('.st, .snippet, .abstract, .description')
            description = self.clean_text(desc_elem.text) if desc_elem else ""

            # Skip low-quality results
            if len(title) < 3 or len(link_url) < 10:
                continue

            results.append({
                'title': title,
                'url': link_url,
                'description': description
            })

        return results

    def _extract_from_bing(self, soup, url):
        """Extract results from Bing search"""
        results = []

        # Find search result elements
        search_results = soup.select('.b_algo, .b_result')

        for result in search_results:
            title_elem = result.select_one('h2')
            link_elem = result.select_one('h2 a')

            if not title_elem or not link_elem:
                continue

            title = self.clean_text(title_elem.text)
            link_url = link_elem.get('href', '')

            # Skip unwanted URLs
            if not link_url or link_url.startswith(('/search', '#', 'javascript:')):
                continue

            # Extract description
            desc_elem = result.select_one('.b_caption p')
            description = self.clean_text(desc_elem.text) if desc_elem else ""

            # Skip low-quality results
            if len(title) < 3 or len(link_url) < 10:
                continue

            results.append({
                'title': title,
                'url': link_url,
                'description': description
            })

        return results

    def _extract_from_ddg(self, soup, url):
        """Extract results from DuckDuckGo search"""
        results = []

        # Find search result elements
        search_results = soup.select('.result, .result__body')

        for result in search_results:
            title_elem = result.select_one('.result__title')
            link_elem = result.select_one('.result__title a')

            if not title_elem or not link_elem:
                continue

            title = self.clean_text(title_elem.text)
            link_url = link_elem.get('href', '')

            # Skip unwanted URLs
            if not link_url or link_url.startswith(('/search', '#', 'javascript:')):
                continue

            # Extract description
            desc_elem = result.select_one('.result__snippet')
            description = self.clean_text(desc_elem.text) if desc_elem else ""

            # Skip low-quality results
            if len(title) < 3 or len(link_url) < 10:
                continue

            results.append({
                'title': title,
                'url': link_url,
                'description': description
            })

        return results

    def _extract_generic(self, soup, url):
        """Generic extraction for unknown search engines"""
        results = []

        # Try to find any elements that might be search results
        potential_results = []

        # Look for common result patterns
        for tag in ['div', 'li', 'article']:
            elements = soup.select(f'{tag} a[href]')
            for elem in elements:
                # Get the parent container
                parent = elem.find_parent(tag)
                if parent:
                    potential_results.append((parent, elem))

        # Process potential results
        for parent, link_elem in potential_results:
            link_url = link_elem.get('href', '')

            # Skip unwanted URLs
            if not link_url or link_url.startswith(('#', 'javascript:')):
                continue

            # Skip internal links
            if link_url.startswith('/') and not link_url.startswith('//'):
                continue

            # Try to get title from the link or its parent
            title = self.clean_text(link_elem.text)
            if not title or len(title) < 5:
                title_elem = parent.select_one('h2, h3, h4, strong')
                if title_elem:
                    title = self.clean_text(title_elem.text)

            # Try to get description
            description = ""
            desc_elem = parent.select_one('p, .description, .snippet')
            if desc_elem:
                description = self.clean_text(desc_elem.text)

            # Only add if we have a title and URL
            if title and len(title) > 5 and len(link_url) > 10:
                # Check if this is likely a search result (has both title and description)
                if description and len(description) > 20:
                    results.append({
                        'title': title,
                        'url': link_url,
                        'description': description
                    })

        return results

    def transform(self, data, url):
        """Transform search results - minimal processing needed"""
        # Filter out duplicates and sort by relevance
        unique_results = []
        seen_urls = set()

        for item in data:
            if not item:
                continue

            if item['url'] in seen_urls:
                continue

            seen_urls.add(item['url'])
            unique_results.append(item)

        # Score results for relevance
        for result in unique_results:
            score = 0

            # Higher score for occult-related terms in title
            occult_terms = ['occult', 'esoteric', 'symbol', 'magic', 'ritual', 'spiritual',
                            'mystic', 'sacred', 'ancient']

            for term in occult_terms:
                if term in result['title'].lower():
                    score += 2
                if term in result['description'].lower():
                    score += 1

            # Higher score for trusted domains
            trusted_domains = ['wikipedia.org', 'sacred-texts.com', 'academia.edu',
                               'jstor.org', 'britannica.com', 'hermetic.com']

            for domain in trusted_domains:
                if domain in result['url']:
                    score += 3

            result['relevance_score'] = score

        # Sort by relevance
        sorted_results = sorted(unique_results, key=lambda x: x['relevance_score'], reverse=True)
        return sorted_results