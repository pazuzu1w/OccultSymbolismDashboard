# scrapers/manager.py
import logging
import json
import os
from datetime import datetime
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from scrapers.symbol_scraper import SymbolScraper
from scrapers.tradition_scraper import TraditionScraper
from scrapers.connection_scraper import ConnectionScraper
from scrapers.search_scraper import SearchScraper

class ScraperManager:
    """Manages multiple scrapers, schedules jobs, and consolidates data"""

    def __init__(self, max_workers=4, existing_data=None):
        self.scrapers = []
        self.visited_urls = set()
        self.max_workers = max_workers
        self.existing_data = existing_data
        self.results = {
            'symbols': [],
            'traditions': [],
            'connections': []
        }
        self.detailed_scrape_queue = []
        self.logger = logging.getLogger('ScraperManager')

    def add_sources(self, sources_config):
        """Add sources to scrape from a configuration"""
        self.logger.info(f"Adding {len(sources_config)} source configurations")

        for config in sources_config:
            source_type = config.get('type', 'generic')
            urls = config.get('urls', [])

            if not urls:
                self.logger.warning(f"Skipping config with no URLs: {config}")
                continue

            self.logger.info(f"Adding {len(urls)} URLs for {source_type} scraper")

            if source_type == 'symbol':
                self.scrapers.append({
                    'type': 'symbol',
                    'urls': urls,
                    'scraper': SymbolScraper(urls=urls)
                })
            elif source_type == 'tradition':
                self.scrapers.append({
                    'type': 'tradition',
                    'urls': urls,
                    'scraper': TraditionScraper(urls=urls)
                })
            elif source_type == 'connection':
                if not self.existing_data:
                    self.logger.warning("Connection scraper needs existing data")
                    continue

                self.scrapers.append({
                    'type': 'connection',
                    'urls': urls,
                    'scraper': ConnectionScraper(
                        existing_symbols=self.existing_data.get('symbols', []),
                        urls=urls
                    )
                })
            else:
                self.logger.warning(f"Unknown scraper type: {source_type}")

    def run_all(self):
        """Run all registered scrapers and consolidate results"""
        if not self.scrapers:
            self.logger.warning("No scrapers registered")
            return self.results

        self.logger.info(f"Running {len(self.scrapers)} scrapers")

        # First run all the registered scrapers
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for scraper_info in self.scrapers:
                futures.append(executor.submit(self._run_scraper, scraper_info))

            # Process results as they complete
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    self.logger.error(f"Error running scraper: {str(e)}")

        # Then process the detailed scrape queue
        if self.detailed_scrape_queue:
            self.logger.info(f"Processing {len(self.detailed_scrape_queue)} detailed scrape requests")
            self._process_detailed_scrape_queue()

        self.logger.info(f"Scraping complete. Found {len(self.results['symbols'])} symbols, "
                         f"{len(self.results['traditions'])} traditions, "
                         f"{len(self.results['connections'])} connections")

        return self.results

    def _run_scraper(self, scraper_info):
        """Run a single scraper and process its results"""
        scraper_type = scraper_info['type']
        scraper = scraper_info['scraper']

        self.logger.info(f"Running {scraper_type} scraper")

        try:
            results = scraper.run()

            if not results:
                self.logger.warning(f"{scraper_type} scraper returned no results")
                return

            self.logger.info(f"{scraper_type} scraper returned {len(results)} results")

            # Process results based on type
            if scraper_type == 'symbol':
                for symbol in results:
                    url = symbol.get('source_url')
                    if url:
                        self.visited_urls.add(url)
                    self.results['symbols'].append(symbol)

                    # If we found new symbols, schedule connection scraping
                    self._maybe_schedule_connection_scraping(symbol)

            elif scraper_type == 'tradition':
                for tradition in results:
                    url = tradition.get('source_url')
                    if url:
                        self.visited_urls.add(url)
                    self.results['traditions'].append(tradition)

                    # Schedule detailed scraping if needed
                    if tradition.get('needs_detailed_scraping'):
                        self._add_to_detailed_scrape_queue(tradition)

            elif scraper_type == 'connection':
                for connection in results:
                    self.results['connections'].append(connection)

        except Exception as e:
            self.logger.error(f"Error in {scraper_type} scraper: {str(e)}")

    def _maybe_schedule_connection_scraping(self, symbol):
        """Decide if we should schedule additional connection scraping for a symbol"""
        # Only schedule if we have enough existing symbols
        if len(self.results['symbols']) > 10:
            name = symbol.get('name', '')
            url = symbol.get('source_url')

            if name and url:
                # Check if we already have a detailed page for this symbol
                parsed_url = urlparse(url)
                if parsed_url.path.endswith(('.html', '.htm')):
                    # Already on a detailed page
                    return

                # Look for a Wikipedia page
                if 'wikipedia.org' in url and '/wiki/' in url:
                    # Already on a Wiki page
                    return

                # Otherwise, schedule a search for this symbol's detailed page
                search_url = f"https://www.google.com/search?q={name.replace(' ', '+')}+occult+symbol"

                self._add_to_detailed_scrape_queue({
                    'type': 'connection',
                    'search_url': search_url,
                    'symbol_name': name,
                    'symbol_id': symbol.get('id')
                })

    def _add_to_detailed_scrape_queue(self, item):
        """Add an item to the detailed scrape queue"""
        # Avoid duplicates
        for existing in self.detailed_scrape_queue:
            if existing.get('symbol_name') == item.get('symbol_name'):
                return
            if existing.get('name') == item.get('name'):
                return

        self.detailed_scrape_queue.append(item)

    def _process_detailed_scrape_queue(self):
        """Process items in the detailed scrape queue"""
        # Group by type for more efficient processing
        queue_by_type = {
            'tradition': [],
            'symbol': [],
            'connection': []
        }

        for item in self.detailed_scrape_queue:
            item_type = item.get('type', 'symbol')  # Default to symbol
            if item_type in queue_by_type:
                queue_by_type[item_type].append(item)

        # Process each type with a dedicated scraper
        for item_type, items in queue_by_type.items():
            if not items:
                continue

            self.logger.info(f"Processing {len(items)} detailed {item_type} items")

            if item_type == 'tradition':
                # Extract URLs
                urls = [item.get('source_url') for item in items if item.get('source_url')]

                # Skip URLs we've already visited
                new_urls = [url for url in urls if url not in self.visited_urls]

                if new_urls:
                    scraper = TraditionScraper(urls=new_urls)
                    results = scraper.run()

                    if results:
                        self.logger.info(f"Found {len(results)} traditions from detailed scraping")
                        for tradition in results:
                            url = tradition.get('source_url')
                            if url:
                                self.visited_urls.add(url)
                            self.results['traditions'].append(tradition)

            elif item_type == 'symbol':
                # Similar to traditions
                urls = [item.get('source_url') for item in items if item.get('source_url')]
                new_urls = [url for url in urls if url not in self.visited_urls]

                if new_urls:
                    scraper = SymbolScraper(urls=new_urls)
                    results = scraper.run()

                    if results:
                        self.logger.info(f"Found {len(results)} symbols from detailed scraping")
                        for symbol in results:
                            url = symbol.get('source_url')
                            if url:
                                self.visited_urls.add(url)
                            self.results['symbols'].append(symbol)

            elif item_type == 'connection':
                # For connections, we need to handle search URLs
                for item in items:
                    search_url = item.get('search_url')
                    if not search_url or search_url in self.visited_urls:
                        continue

                    # First, find potential detailed pages
                    from .search_scraper import SearchScraper

                    search_scraper = SearchScraper(url=search_url)
                    search_results = search_scraper.run()

                    if not search_results:
                        continue

                    # Take top 3 results
                    top_urls = [r.get('url') for r in search_results[:3] if r.get('url')]
                    new_urls = [url for url in top_urls if url not in self.visited_urls]

                    if new_urls:
                        # Now scrape these pages for connections
                        connection_scraper = ConnectionScraper(
                            existing_symbols=self.results['symbols'] + (
                                self.existing_data.get('symbols', []) if self.existing_data else []),
                            urls=new_urls
                        )

                        results = connection_scraper.run()

                        if results:
                            self.logger.info(f"Found {len(results)} connections from detailed scraping")
                            for connection in results:
                                self.results['connections'].append(connection)

                        # Mark these URLs as visited
                        for url in new_urls:
                            self.visited_urls.add(url)

            elif item_type == 'connection':
                try:
                    from .search_scraper import SearchScraper
                except ImportError:
                    self.logger.error("SearchScraper module not found")
                    continue

    def save_results(self, output_path='data/scraped_data.json'):
        """Save the scraped results to a file"""
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                'symbols': self.results['symbols'],
                'traditions': self.results['traditions'],
                'connections': self.results['connections'],
                'metadata': {
                    'scrape_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'urls_visited': list(self.visited_urls),
                    'total_symbols': len(self.results['symbols']),
                    'total_traditions': len(self.results['traditions']),
                    'total_connections': len(self.results['connections'])
                }
            }, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Results saved to {output_path}")