# scrapers/tradition_scraper.py
from .base_scraper import BaseScraper
import re
from datetime import datetime
import hashlib


class TraditionScraper(BaseScraper):
    """Specialized scraper for occult traditions"""

    def __init__(self, url=None, urls=None, headers=None, proxies=None):
        super().__init__(url, urls, headers, proxies)

        # Map of common era abbreviations
        self.era_map = {
            'bce': -1, 'bc': -1, 'b.c.e.': -1, 'b.c.': -1,
            'ce': 1, 'ad': 1, 'c.e.': 1, 'a.d.': 1,
        }

        # Regions mapping
        self.region_map = {
            'egypt': 'North Africa',
            'north africa': 'North Africa',
            'greece': 'Mediterranean',
            'mediterranean': 'Mediterranean',
            'rome': 'Mediterranean',
            'italy': 'Mediterranean',
            'middle east': 'Middle East',
            'persia': 'Middle East',
            'mesopotamia': 'Middle East',
            'israel': 'Middle East',
            'palestine': 'Middle East',
            'judea': 'Middle East',
            'babylon': 'Middle East',
            'europe': 'Europe',
            'western europe': 'Europe',
            'central europe': 'Europe',
            'eastern europe': 'Europe',
            'scandinavia': 'Scandinavia',
            'norse': 'Scandinavia',
            'nordic': 'Scandinavia',
            'celtic': 'Western Europe',
            'britain': 'Western Europe',
            'ireland': 'Western Europe',
            'scotland': 'Western Europe',
            'france': 'Western Europe',
            'germany': 'Central Europe',
            'china': 'East Asia',
            'japan': 'East Asia',
            'east asia': 'East Asia',
            'india': 'South Asia',
            'south asia': 'South Asia',
            'america': 'North America',
            'north america': 'North America',
            'usa': 'North America',
            'united states': 'North America',
            'global': 'Global',
        }

    def extract(self, soup, url):
        """Extract tradition data from the page"""
        self.logger.info(f"Extracting tradition data from {url}")

        if not soup:
            return None

        traditions = []

        try:
            # Different extraction strategies based on website structure
            if 'wikipedia.org' in url:
                traditions = self._extract_from_wikipedia(soup, url)
            elif 'sacred-texts.com' in url:
                traditions = self._extract_from_sacred_texts(soup, url)
            else:
                # Generic extraction for unknown sites
                traditions = self._extract_generic(soup, url)

            self.logger.info(f"Extracted {len(traditions)} traditions from {url}")
            return traditions

        except Exception as e:
            self.logger.error(f"Error extracting from {url}: {str(e)}")
            return []

    def _extract_from_wikipedia(self, soup, url):
        """Extract tradition data from Wikipedia pages"""
        traditions = []

        # Method 1: Extract from infoboxes and headings
        title_elem = soup.select_one('h1#firstHeading')
        title = self.clean_text(title_elem.text) if title_elem else "Unknown Tradition"

        tradition = {'name': title, 'source_url': url}

        # Extract from infobox if present
        infobox = soup.select_one('.infobox')
        if infobox:
            # Try to extract period
            period_row = self._find_infobox_row(infobox, 'Period')
            if period_row:
                period_text = self.clean_text(period_row.text)
                date_range = self._extract_date_range(period_text)
                if date_range:
                    tradition['start_century'] = date_range[0]
                    tradition['end_century'] = date_range[1]

            # Try to extract region
            region_row = self._find_infobox_row(infobox, 'Region')
            if region_row:
                region_text = self.clean_text(region_row.text)
                tradition['region'] = self._normalize_region(region_text)

            # Try to extract major texts
            texts_row = self._find_infobox_row(infobox, 'Texts')
            if texts_row:
                texts = [self.clean_text(li.text) for li in texts_row.select('li')]
                if texts:
                    tradition['major_texts'] = texts

            # Try to extract key figures
            figures_row = self._find_infobox_row(infobox, 'Figures') or self._find_infobox_row(infobox, 'Notable')
            if figures_row:
                figures = [self.clean_text(li.text) for li in figures_row.select('li')]
                if not figures:  # If no list items, try comma separation
                    figures_text = self.clean_text(figures_row.text)
                    figures = [f.strip() for f in figures_text.split(',')]
                if figures:
                    tradition['key_figures'] = figures

        # Extract description from first paragraph
        first_para = soup.select_one('#mw-content-text > .mw-parser-output > p')
        if first_para:
            tradition['description'] = self.clean_text(first_para.text)

            # Try to extract period and region from description if not found
            if 'start_century' not in tradition or 'end_century' not in tradition:
                date_range = self._extract_date_range(tradition['description'])
                if date_range:
                    tradition['start_century'] = date_range[0]
                    tradition['end_century'] = date_range[1]

            if 'region' not in tradition:
                tradition['region'] = self._extract_region_from_text(tradition['description'])

        # Extract core concepts from headings and following paragraphs
        concept_headings = soup.select('h2, h3')
        core_concepts = []

        for heading in concept_headings:
            heading_text = self.clean_text(heading.text)

            # Look for concept-related headings
            if any(term in heading_text.lower() for term in [
                'concept', 'belief', 'teaching', 'principle', 'doctrine', 'idea', 'philosophy']):

                # Get concepts from paragraphs following heading
                next_paras = []
                next_elem = heading.find_next('p')
                while next_elem and next_elem.name == 'p':
                    next_paras.append(next_elem)
                    next_elem = next_elem.find_next_sibling()

                # Extract concepts from these paragraphs
                for para in next_paras:
                    para_text = self.clean_text(para.text)
                    concepts = self._extract_concepts_from_text(para_text)
                    if concepts:
                        core_concepts.extend(concepts)

        if core_concepts:
            tradition['core_concepts'] = list(set(core_concepts))  # Remove duplicates

        # Add tradition if we have minimal required info
        if 'name' in tradition and ('description' in tradition or 'core_concepts' in tradition):
            traditions.append(tradition)

        # Also check for list of related traditions
        tradition_links = []
        for section in soup.select('h2, h3, h4'):
            section_text = self.clean_text(section.text).lower()
            if any(term in section_text for term in ['tradition', 'school', 'branch', 'movement']):
                # Find lists following this section
                next_elem = section.find_next(['ul', 'ol'])
                if next_elem:
                    for li in next_elem.select('li'):
                        link = li.select_one('a')
                        if link:
                            trad_name = self.clean_text(link.text)
                            if trad_name and len(trad_name) > 3:
                                tradition_links.append({
                                    'name': trad_name,
                                    'source_url': 'https://en.wikipedia.org' + link.get('href') if link.get(
                                        'href').startswith('/') else link.get('href'),
                                    'needs_detailed_scraping': True  # Flag to scrape this tradition in detail later
                                })

        # Add the related traditions to our results
        traditions.extend(tradition_links)

        return traditions

    def _extract_from_sacred_texts(self, soup, url):
        """Extract tradition data from sacred-texts.com"""
        traditions = []

        # Try to get main tradition from title
        title_elem = soup.select_one('h1, h2, title')
        title = self.clean_text(title_elem.text) if title_elem else "Unknown Tradition"

        # Clean up title
        if ':' in title:
            title = title.split(':', 1)[0].strip()

        if 'Sacred Texts' in title:
            title = title.replace('Sacred Texts', '').strip()

        tradition = {'name': title, 'source_url': url}

        # Extract main content
        main_content = soup.select_one('main, #content, .content, article, .text')
        if not main_content:
            main_content = soup

        # Get description from first paragraphs
        paras = main_content.select('p')
        if paras:
            description = self.clean_text(paras[0].text)
            if len(paras) > 1:
                description += ' ' + self.clean_text(paras[1].text)
            tradition['description'] = description

            # Try to extract period and region from description
            date_range = self._extract_date_range(description)
            if date_range:
                tradition['start_century'] = date_range[0]
                tradition['end_century'] = date_range[1]

            tradition['region'] = self._extract_region_from_text(description)

        # Look for major texts
        major_texts = []
        text_headings = main_content.select('h2, h3, h4')

        for heading in text_headings:
            heading_text = self.clean_text(heading.text).lower()

            if any(term in heading_text for term in ['text', 'book', 'scripture', 'writing']):
                # Look for lists after this heading
                next_elem = heading.find_next(['ul', 'ol'])
                if next_elem:
                    for li in next_elem.select('li'):
                        text_name = self.clean_text(li.text)
                        if text_name and len(text_name) > 3:
                            major_texts.append(text_name)

        if major_texts:
            tradition['major_texts'] = major_texts

        # Extract core concepts
        core_concepts = []

        for para in paras:
            para_text = self.clean_text(para.text)
            concepts = self._extract_concepts_from_text(para_text)
            if concepts:
                core_concepts.extend(concepts)

        if core_concepts:
            tradition['core_concepts'] = list(set(core_concepts[:10]))  # Limit to 10 unique concepts

        # Add tradition if we have minimal required info
        if 'name' in tradition and ('description' in tradition or 'major_texts' in tradition):
            traditions.append(tradition)

        return traditions

    def _extract_generic(self, soup, url):
        """Generic extraction for unknown site structures"""
        traditions = []

        # Try to get main tradition from title
        title_elem = soup.select_one('h1, h2, title')
        title = self.clean_text(title_elem.text) if title_elem else ""

        # Only process if title seems like a tradition
        if self._looks_like_tradition(title):
            tradition = {'name': title, 'source_url': url}

            # Get main content
            main_content = soup.select_one('main, #content, .content, article')
            if not main_content:
                main_content = soup

            # Get description from first paragraphs
            paras = main_content.select('p')
            if paras:
                for para in paras[:3]:  # Look at first 3 paragraphs
                    para_text = self.clean_text(para.text)
                    if len(para_text) > 100:  # Only substantial paragraphs
                        tradition['description'] = para_text
                        break

                # Try to extract period and region
                if 'description' in tradition:
                    date_range = self._extract_date_range(tradition['description'])
                    if date_range:
                        tradition['start_century'] = date_range[0]
                        tradition['end_century'] = date_range[1]

                    tradition['region'] = self._extract_region_from_text(tradition['description'])

                # Extract core concepts
                core_concepts = []

                for para in paras:
                    para_text = self.clean_text(para.text)
                    concepts = self._extract_concepts_from_text(para_text)
                    if concepts:
                        core_concepts.extend(concepts)

                if core_concepts:
                    tradition['core_concepts'] = list(set(core_concepts[:10]))

            # Add tradition if we have minimal required info
            if 'name' in tradition and 'description' in tradition:
                traditions.append(tradition)

        # Also look for other tradition names on the page
        for heading in soup.select('h1, h2, h3, h4'):
            heading_text = self.clean_text(heading.text)

            if self._looks_like_tradition(heading_text) and heading_text != title:
                # Find description in following paragraph
                next_para = heading.find_next('p')
                if next_para:
                    para_text = self.clean_text(next_para.text)
                    if len(para_text) > 100:
                        traditions.append({
                            'name': heading_text,
                            'description': para_text,
                            'source_url': url
                        })

        return traditions

    def _looks_like_tradition(self, text):
        """Check if a text string likely represents an occult tradition"""
        if not text:
            return False

        # Common terms indicating traditions
        tradition_terms = [
            'occult', 'esoteric', 'mystical', 'spiritual', 'hermetic', 'alchemical',
            'magical', 'magick', 'pagan', 'wicca', 'druid', 'kabbalah', 'gnostic',
            'theosophy', 'rosicrucian', 'masonic', 'ceremonial magic', 'grimoire',
            'witchcraft', 'sorcery', 'shamanism', 'tantra', 'vedic', 'mystery cult',
            'theurgy', 'alchemy', 'astrology', 'divination', 'magician', 'ritual',
            'initiation', 'thelema', 'golden dawn', 'enochian', 'hermeticism'
        ]

        text_lower = text.lower()

        for term in tradition_terms:
            if term in text_lower:
                return True

        # Check for common tradition names
        tradition_names = [
            'egyptian', 'greek', 'roman', 'norse', 'celtic', 'druidic',
            'kabbalah', 'hermetic', 'rosicrucian', 'masonic', 'thelemic',
            'wiccan', 'neopagan', 'golden dawn', 'oto', 'chaos magic',
            'enochian', 'grimoire', 'goetia', 'theosophical'
        ]

        for name in tradition_names:
            if name in text_lower:
                return True

        return False

    def _find_infobox_row(self, infobox, header_text):
        """Helper to find infobox row by header text"""
        rows = infobox.select('tr')
        for row in rows:
            header = row.select_one('th')
            if header and header_text.lower() in header.text.lower():
                return row.select_one('td')
        return None

    def _extract_date_range(self, text):
        """Extract date range from text (returns start and end centuries)"""
        if not text:
            return None

        text = text.lower()

        # Pattern for century spans like "5th-10th century"
        century_span_pattern = r'(\d+)(?:st|nd|rd|th)?\s*[-–—]\s*(\d+)(?:st|nd|rd|th)?\s+(?:century|cent\.)'

        # Pattern for single centuries with era like "5th century BCE"
        single_century_pattern = r'(\d+)(?:st|nd|rd|th)?\s+(?:century|cent\.)\s+(bce|bc|ce|ad|b\.c\.e\.|b\.c\.|c\.e\.|a\.d\.)'

        # Pattern for year ranges like "500 BCE - 400 CE"
        year_span_pattern = r'(\d+)\s*(bce|bc|ce|ad|b\.c\.e\.|b\.c\.|c\.e\.|a\.d\.)?(?:\s*[-–—]\s*)(\d+)\s*(bce|bc|ce|ad|b\.c\.e\.|b\.c\.|c\.e\.|a\.d\.)'

        # Try century span first
        century_match = re.search(century_span_pattern, text)
        if century_match:
            start_century = int(century_match.group(1))
            end_century = int(century_match.group(2))

            # Assume CE unless BCE/BC appears nearby
            era_modifier = -1 if re.search(r'bce|bc|b\.c\.e\.|b\.c\.', text[:century_match.start() + 30]) else 1

            return start_century * era_modifier, end_century * era_modifier

        # Try single century with era
        single_match = re.search(single_century_pattern, text)
        if single_match:
            century = int(single_match.group(1))
            era = single_match.group(2).lower()

            # Convert era to modifier
            era_modifier = self.era_map.get(era, 1)  # Default to CE
            start_century = century * era_modifier

            # For ancient traditions, use a reasonable span
            if era_modifier < 0:  # BCE
                end_century = start_century + 5
            else:  # CE
                end_century = min(21, start_century + 5)  # Cap at 21st century

            return start_century, end_century

        # Try year ranges
        year_match = re.search(year_span_pattern, text)
        if year_match:
            start_year = int(year_match.group(1))
            start_era = year_match.group(2)
            end_year = int(year_match.group(3))
            end_era = year_match.group(4)

            # Convert to century
            start_century = (start_year // 100) + (1 if start_year % 100 > 0 else 0)
            end_century = (end_year // 100) + (1 if end_year % 100 > 0 else 0)

            # Apply era modifiers
            if start_era:
                start_modifier = self.era_map.get(start_era.lower(), 1)
                start_century *= start_modifier

            if end_era:
                end_modifier = self.era_map.get(end_era.lower(), 1)
                end_century *= end_modifier

            return start_century, end_century

        # If no clear date range found, try to extract any century mentioned
        century_mentions = re.findall(r'(\d+)(?:st|nd|rd|th)?\s+(?:century|cent\.)', text)
        if century_mentions:
            century = int(century_mentions[0])

            # Check if it's BCE/BC
            era_modifier = -1 if re.search(r'bce|bc|b\.c\.e\.|b\.c\.', text) else 1
            start_century = century * era_modifier

            # For ancient traditions, use a reasonable span
            if era_modifier < 0:  # BCE
                end_century = start_century + 5
            else:  # CE
                end_century = min(21, start_century + 5)  # Cap at 21st century

            return start_century, end_century

        # If we still don't have a date, extract modern vs ancient
        if any(term in text for term in ['modern', 'contemporary', 'current', 'today', 'present']):
            return 20, 21  # 20th-21st century
        elif any(term in text for term in ['ancient', 'antiquity', 'classical']):
            return -5, 5  # Roughly 500 BCE to 500 CE
        elif 'medieval' in text:
            return 5, 15  # 5th-15th century CE
        elif 'renaissance' in text:
            return 14, 17  # 14th-17th century CE

        # Default to unknown
        return None

    def _normalize_region(self, region_text):
        """Normalize region names"""
        if not region_text:
            return "Unknown"

        region_text = region_text.lower()

        # Check for direct matches in our mapping
        for key, value in self.region_map.items():
            if key in region_text:
                return value

        # Check for multi-region text
        regions = []
        for key, value in self.region_map.items():
            if key in region_text and value not in regions:
                regions.append(value)

        if regions:
            return '/'.join(regions)

        # Default
        return "Unknown"

    def _extract_region_from_text(self, text):
        """Extract region information from descriptive text"""
        if not text:
            return "Unknown"

        text = text.lower()

        # Look for region mentions
        regions = []
        for key, value in self.region_map.items():
            if key in text and value not in regions:
                regions.append(value)

        if regions:
            return '/'.join(regions)

        return "Unknown"

    def _extract_concepts_from_text(self, text):
        """Extract key concepts from text"""
        if not text:
            return []

        concepts = []

        # Look for explicit concept indicators
        concept_patterns = [
            r'concept of ([^,.;:]+)',
            r'principle of ([^,.;:]+)',
            r'belief in ([^,.;:]+)',
            r'doctrine of ([^,.;:]+)',
            r'idea of ([^,.;:]+)',
            r'central to .+ (?:was|is) ([^,.;:]+)',
            r'based on ([^,.;:]+)',
            r'focused on ([^,.;:]+)',
            r'emphasizes ([^,.;:]+)',
            r'practices include ([^,.;:]+)',
        ]

        for pattern in concept_patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                concept = self.clean_text(match.group(1))
                if concept and len(concept) > 3 and len(concept) < 40:
                    concepts.append(concept.capitalize())

        # Look for capitalized phrases that might be concepts
        cap_phrases = re.findall(r'[A-Z][a-z]+ (?:[A-Z][a-z]+ ){0,3}[A-Z][a-z]+', text)
        for phrase in cap_phrases:
            if 6 < len(phrase) < 40 and ' ' in phrase:  # Multi-word phrases only
                concepts.append(phrase)

        return concepts[:15]  # Limit to 15 concepts

    def transform(self, data, url):
        """Transform scraped tradition data to match our Tradition model"""
        self.logger.info(f"Transforming {len(data)} traditions from {url}")

        transformed = []

        for item in data:
            if not item:
                continue

            # Skip items flagged for detailed scraping
            if item.get('needs_detailed_scraping'):
                continue

            # Generate a unique name
            name = item.get('name', 'Unknown Tradition')

            # Set reasonable defaults for missing data
            if 'start_century' not in item or 'end_century' not in item:
                # If we have a description, try to extract date range
                if 'description' in item:
                    date_range = self._extract_date_range(item['description'])
                    if date_range:
                        item['start_century'], item['end_century'] = date_range
                    else:
                        # Default to a reasonable range based on name
                        if self._looks_like_modern_tradition(name):
                            item['start_century'] = 19
                            item['end_century'] = 21
                        else:
                            item['start_century'] = -5
                            item['end_century'] = 5
                else:
                    # Default values if no description
                    item['start_century'] = 0
                    item['end_century'] = 21

            # Ensure we have region
            if 'region' not in item or item['region'] == "Unknown":
                if 'description' in item:
                    item['region'] = self._extract_region_from_text(item['description'])
                else:
                    item['region'] = "Unknown"

            # Ensure we have major texts
            if 'major_texts' not in item or not item['major_texts']:
                item['major_texts'] = ["Unknown"]

            # Create the transformed tradition
            transformed_item = {
                'name': name,
                'start_century': item['start_century'],
                'end_century': item['end_century'],
                'region': item['region'],
                'major_texts': item.get('major_texts', ["Unknown"]),
                'key_figures': item.get('key_figures', []),
                'core_concepts': item.get('core_concepts', []),
                'source_url': item.get('source_url', url),
                'date_added': datetime.now().strftime('%Y-%m-%d'),
            }

            # Add if it's valid
            if self._validate_tradition(transformed_item):
                transformed.append(transformed_item)

        self.logger.info(f"Transformed {len(transformed)} valid traditions")
        return transformed

    def _looks_like_modern_tradition(self, name):
        """Check if a tradition name appears to be modern"""
        modern_indicators = [
            'chaos magic', 'thelema', 'wicca', 'neo-pagan', 'neopagan',
            'new age', 'modern', 'contemporary', 'discordian', 'satanism',
            'golden dawn', 'oto', 'theosophical'
        ]

        name_lower = name.lower()
        for indicator in modern_indicators:
            if indicator in name_lower:
                return True

        return False

    def _validate_tradition(self, tradition):
        """Validate a tradition before adding it to results"""
        # Check for duplicates
        for existing in self.results:
            if existing['name'].lower() == tradition['name'].lower():
                return False

        # Basic validation
        if len(tradition['name']) < 3:
            return False

        return True