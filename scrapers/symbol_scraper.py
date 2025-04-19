# scrapers/symbol_scraper.py
from .base_scraper import BaseScraper
import re
from datetime import datetime
import hashlib


class SymbolScraper(BaseScraper):
    """Specialized scraper for occult symbols"""

    def __init__(self, url=None, urls=None, headers=None, proxies=None):
        super().__init__(url, urls, headers, proxies)
        # Map to convert text century representations to numeric values
        self.century_map = {
            'BCE': -1,  # Multiplier for BCE dates
            'CE': 1,  # Multiplier for CE dates
            'BC': -1,  # Alternative notation
            'AD': 1,  # Alternative notation
            'century': 100,  # Convert century to year
            'millennia': 1000,  # Convert millennia to year
        }

    def extract(self, soup, url):
        """Extract occult symbol data from the page"""
        self.logger.info(f"Extracting data from {url}")

        if not soup:
            return None

        symbols = []

        try:
            # Different extraction strategies based on website structure
            if 'wikipedia.org' in url:
                symbols = self._extract_from_wikipedia(soup, url)
            elif 'sacred-texts.com' in url:
                symbols = self._extract_from_sacred_texts(soup, url)
            else:
                # Generic extraction for unknown sites
                symbols = self._extract_generic(soup, url)

            self.logger.info(f"Extracted {len(symbols)} symbols from {url}")
            return symbols

        except Exception as e:
            self.logger.error(f"Error extracting from {url}: {str(e)}")
            return []

    def _extract_from_wikipedia(self, soup, url):
        """Extract symbol data from Wikipedia pages"""
        symbols = []

        # Method 1: Extract from infoboxes
        info_boxes = soup.select('.infobox')
        for box in info_boxes:
            symbol = {'source_url': url}

            # Extract name from page title or infobox title
            title_elem = soup.select_one('h1#firstHeading') or box.select_one('.infobox-title')
            if title_elem:
                symbol['name'] = self.clean_text(title_elem.text)

            # Extract properties from infobox rows
            properties = [
                ('Tradition', 'tradition'),
                ('Origin', 'origin'),
                ('Element', 'element'),
                ('Symbol of', 'description'),
                ('Used for', 'usage'),
                ('Used by', 'used_by'),
                ('Period', 'period'),
            ]

            for label, key in properties:
                row = self._find_infobox_row(box, label)
                if row:
                    symbol[key] = self.clean_text(row.text)

            # Extract description from first paragraph
            if 'description' not in symbol or not symbol['description']:
                first_para = soup.select_one('#mw-content-text > .mw-parser-output > p')
                if first_para:
                    symbol['description'] = self.clean_text(first_para.text)

            # Only add if we have at least a name and some other data
            if symbol.get('name') and len(symbol) > 2:
                symbols.append(symbol)

        # Method 2: Extract from list items (for category pages)
        if not symbols:
            list_items = soup.select('div.mw-category li a, ul.gallery li a')
            for item in list_items:
                name = self.clean_text(item.text)
                if name and len(name) > 2:  # Basic validation
                    symbol_url = item.get('href')
                    if symbol_url and not symbol_url.startswith(('http://', 'https://')):
                        symbol_url = 'https://en.wikipedia.org' + symbol_url

                    symbols.append({
                        'name': name,
                        'source_url': symbol_url or url,
                        'needs_detailed_scraping': True  # Flag to scrape detailed page later
                    })

        return symbols

    def _extract_from_sacred_texts(self, soup, url):
        """Extract symbol data from sacred-texts.com"""
        symbols = []

        # Extract from article content
        article = soup.select_one('article, .text, .content')
        if not article:
            article = soup  # Fall back to entire page

        # Find headings that might indicate symbol names
        headings = article.select('h1, h2, h3, h4, h5, h6, strong, b')

        for heading in headings:
            heading_text = self.clean_text(heading.text)

            # Skip very short headings or navigation elements
            if len(heading_text) < 3 or heading_text.lower() in ['next', 'previous', 'contents', 'index']:
                continue

            # Get the paragraph following the heading
            description = ""
            next_elem = heading.find_next(['p', 'div'])
            if next_elem:
                description = self.clean_text(next_elem.text)

            # Create symbol entry if we have enough info
            if heading_text and description and len(description) > 30:
                symbols.append({
                    'name': heading_text,
                    'description': description,
                    'source_url': url
                })

        return symbols

    def _extract_generic(self, soup, url):
        """Generic extraction for unknown site structures"""
        symbols = []

        # Try to find the main content area
        main_content = soup.select_one('main, #content, .content, article, .post')
        if not main_content:
            main_content = soup

        # Look for headings and lists that might contain symbol information
        headings = main_content.select('h1, h2, h3, h4, h5')
        for heading in headings:
            heading_text = self.clean_text(heading.text)

            # Skip very short or common navigation headings
            if len(heading_text) < 3 or heading_text.lower() in ['menu', 'navigation', 'search']:
                continue

            # Get content following the heading
            description = ""
            next_elem = heading.find_next(['p', 'div', 'section'])
            if next_elem:
                description = self.clean_text(next_elem.text)

            # Basic check if this might be a symbol
            occult_terms = ['symbol', 'sign', 'occult', 'esoteric', 'mystical', 'spiritual',
                            'alchemical', 'magical', 'sacred', 'ancient', 'ritual']

            is_potential_symbol = False
            heading_lower = heading_text.lower()
            description_lower = description.lower()

            for term in occult_terms:
                if term in heading_lower or term in description_lower:
                    is_potential_symbol = True
                    break

            if is_potential_symbol and len(description) > 40:
                symbols.append({
                    'name': heading_text,
                    'description': description,
                    'source_url': url
                })

        return symbols

    def transform(self, data, url):
        """Transform scraped data to match our Symbol model"""
        self.logger.info(f"Transforming {len(data)} symbols from {url}")

        transformed = []

        for item in data:
            if not item:
                continue

            # Generate a deterministic ID based on name and source
            name = item.get('name', 'Unknown')
            source = item.get('source_url', url)
            id_string = f"{name}|{source}"
            hash_object = hashlib.md5(id_string.encode())
            # Use last 9 digits of hash as numeric ID (to avoid collisions with existing IDs)
            symbol_id = int(hash_object.hexdigest(), 16) % 10 ** 9

            # Extract century from text
            century_origin = self._extract_century(
                item.get('origin', '') or
                item.get('period', '') or
                item.get('date', '')
            )

            # Extract element if present
            element = self._extract_element(item)

            # Extract visual elements if described
            visual_elements = self._extract_visual_elements(item)

            # Extract tradition info
            tradition = self._normalize_tradition(item.get('tradition', 'Unknown'))

            transformed_item = {
                'id': symbol_id,
                'name': name,
                'tradition': tradition,
                'element': element or 'Unknown',
                'century_origin': century_origin,
                'description': item.get('description', ''),
                'usage': item.get('usage', ''),
                'visual_elements': visual_elements,
                'source_url': source,
                'date_added': datetime.now().strftime('%Y-%m-%d'),
            }

            # Add only if we have sufficient, valid data
            if self._validate_symbol(transformed_item):
                transformed.append(transformed_item)

        self.logger.info(f"Transformed {len(transformed)} valid symbols")
        return transformed

    def _find_infobox_row(self, infobox, header_text):
        """Helper to find infobox row by header text"""
        rows = infobox.select('tr')
        for row in rows:
            header = row.select_one('th')
            if header and header_text.lower() in header.text.lower():
                return row.select_one('td')
        return None

    def _extract_century(self, text):
        """Extract century information from text"""
        if not text:
            return 0

        text = text.lower()

        # Look for common patterns like "5th century BCE" or "300 BC"
        century_pattern = r'(\d+(?:st|nd|rd|th)?\s+century\s+(?:bce|bc|ce|ad)?)'
        year_pattern = r'(\d+\s+(?:bce|bc|ce|ad))'

        century_match = re.search(century_pattern, text)
        year_match = re.search(year_pattern, text)

        if century_match:
            century_text = century_match.group(1)

            # Extract the number
            num_match = re.search(r'(\d+)', century_text)
            if not num_match:
                return 0

            century_num = int(num_match.group(1))

            # Determine era (BCE/CE)
            era_multiplier = -1 if ('bce' in century_text or 'bc' in century_text) else 1

            return century_num * era_multiplier

        elif year_match:
            year_text = year_match.group(1)

            # Extract the number
            num_match = re.search(r'(\d+)', year_text)
            if not num_match:
                return 0

            year = int(num_match.group(1))

            # Determine era (BCE/CE)
            era_multiplier = -1 if ('bce' in year_text or 'bc' in year_text) else 1

            # Convert year to century
            century = (year // 100) * era_multiplier
            if era_multiplier < 0 and year % 100 > 0:
                century -= 1  # BCE centuries round up

            return century

        return 0

    def _extract_element(self, item):
        """Extract and normalize element information"""
        # Check if we have a direct element field
        element = item.get('element', '')

        if element:
            return element

        # Try to infer from description or other fields
        description = item.get('description', '').lower()

        # Look for common elements in description
        elements = ['fire', 'water', 'earth', 'air', 'spirit', 'life', 'death',
                    'protection', 'knowledge', 'balance', 'transformation']

        for elem in elements:
            if elem in description:
                return elem.capitalize()

        return "Unknown"

    def _extract_visual_elements(self, item):
        """Extract visual elements from description"""
        visual_elements = []

        description = item.get('description', '').lower()

        # Look for visual element descriptions
        visual_patterns = [
            r'depicting (?:a |an )?([^,.;]+)',
            r'showing (?:a |an )?([^,.;]+)',
            r'consists of (?:a |an )?([^,.;]+)',
            r'represents (?:a |an )?([^,.;]+)',
            r'shaped like (?:a |an )?([^,.;]+)',
            r'form of (?:a |an )?([^,.;]+)',
        ]

        for pattern in visual_patterns:
            matches = re.finditer(pattern, description)
            for match in matches:
                element = self.clean_text(match.group(1))
                if element and len(element) > 3:
                    visual_elements.append(element)

        return visual_elements

    def _normalize_tradition(self, tradition):
        """Normalize tradition names"""
        if not tradition or tradition == 'Unknown':
            return 'Unknown'

        # Mapping of variations to standard names
        tradition_map = {
            'egyptian': 'Egyptian',
            'egypt': 'Egyptian',
            'ancient egypt': 'Egyptian',
            'greco': 'Greek',
            'greek': 'Greek',
            'ancient greek': 'Greek',
            'hellenic': 'Greek',
            'roman': 'Roman',
            'hebrew': 'Judaic',
            'jewish': 'Judaic',
            'judaism': 'Judaic',
            'kabbalah': 'Kabbalah',
            'qabbalah': 'Kabbalah',
            'cabala': 'Kabbalah',
            'norse': 'Norse',
            'viking': 'Norse',
            'scandinavian': 'Norse',
            'celtic': 'Celtic',
            'druidic': 'Celtic',
            'taoist': 'Taoist',
            'taoism': 'Taoist',
            'buddhist': 'Buddhist',
            'buddhism': 'Buddhist',
            'hindu': 'Hindu',
            'hinduism': 'Hindu',
            'hermetic': 'Hermetic',
            'hermeticism': 'Hermetic',
            'alchemical': 'Alchemy',
            'alchemy': 'Alchemy',
            'rosicrucian': 'Rosicrucian',
            'masonic': 'Masonic',
            'freemasonry': 'Masonic',
            'wiccan': 'Neo-Pagan',
            'wicca': 'Neo-Pagan',
            'pagan': 'Neo-Pagan',
            'neopagan': 'Neo-Pagan',
            'chaos magic': 'Chaos Magic',
            'chaos magick': 'Chaos Magic',
            'thelemic': 'Thelema',
            'thelema': 'Thelema',
            'christian': 'Christian',
            'christianity': 'Christian',
            'gnostic': 'Gnostic',
            'gnosticism': 'Gnostic',
        }

        # Check for matches
        tradition_lower = tradition.lower()

        for key, value in tradition_map.items():
            if key in tradition_lower:
                return value

        # Handle multi-tradition entries
        traditions = []
        for key, value in tradition_map.items():
            if key in tradition_lower and value not in traditions:
                traditions.append(value)

        if traditions:
            return '/'.join(traditions)

        # If no match found, capitalize the first letter of each word
        return ' '.join(word.capitalize() for word in tradition.split())

    def _validate_symbol(self, symbol):
        """Validate a symbol entry before adding to results"""
        # Name is required
        if not symbol['name'] or len(symbol['name']) < 2:
            return False

        # Description should have some substance
        if not symbol['description'] or len(symbol['description']) < 30:
            return False

        # Check for duplicates or similar entries in our results
        for existing in self.results:
            if existing['name'].lower() == symbol['name'].lower():
                return False

        return True