# scrapers/connection_scraper.py
from .base_scraper import BaseScraper
import re
import itertools
import hashlib
import nltk
from nltk.tokenize import sent_tokenize
import spacy
import datetime

# Download necessary NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Load spaCy model
try:
    nlp = spacy.load('en_core_web_sm')
except:
    # If model not available, use a simpler approach
    nlp = None


class ConnectionScraper(BaseScraper):
    """Scraper for detecting connections between occult symbols"""

    def __init__(self, existing_symbols=None, url=None, urls=None, headers=None, proxies=None):
        super().__init__(url, urls, headers, proxies)
        # Existing symbols to look for connections between
        self.existing_symbols = existing_symbols or []
        # Map symbol names to IDs for quick lookup
        self.symbol_map = {s['name'].lower(): s['id'] for s in self.existing_symbols}
        # Alternative names/spellings for symbols
        self.symbol_aliases = self._build_aliases()

    def _build_aliases(self):
        """Build a dictionary of alternative names for symbols"""
        aliases = {}

        for symbol in self.existing_symbols:
            name = symbol['name'].lower()
            symbol_id = symbol['id']

            # Add original name
            if name not in aliases:
                aliases[name] = symbol_id

            # Add variations
            variations = []

            # Remove special characters
            clean_name = re.sub(r'[^\w\s]', '', name)
            if clean_name != name:
                variations.append(clean_name)

            # Remove "the" prefix
            if name.startswith('the '):
                variations.append(name[4:])

            # Handle hyphenation variations
            if '-' in name:
                variations.append(name.replace('-', ' '))
                variations.append(name.replace('-', ''))

            # Add common spelling variations
            if 'ankh' in name:
                variations.append('key of life')
                variations.append('crux ansata')

            if 'eye of horus' in name:
                variations.append('eye of ra')
                variations.append('wadjet')

            if 'pentagram' in name:
                variations.append('pentacle')
                variations.append('five pointed star')

            # Add aliases to the dictionary
            for alias in variations:
                if alias and alias not in aliases:
                    aliases[alias] = symbol_id

        return aliases

    def extract(self, soup, url):
        """Extract connection data from web pages"""
        self.logger.info(f"Extracting connection data from {url}")

        if not soup:
            return None

        connections = []

        try:
            # Get the main content
            main_content = soup.select_one('main, #content, .content, article, .post')
            if not main_content:
                main_content = soup

            # Extract text from paragraphs
            paragraphs = main_content.select('p')
            text = ' '.join([p.get_text() for p in paragraphs])

            # Extract connections
            if nlp:
                # Use spaCy for more advanced NLP if available
                connections = self._extract_connections_spacy(text)
            else:
                # Fall back to simpler approach
                connections = self._extract_connections_basic(text)

            self.logger.info(f"Extracted {len(connections)} potential connections")
            return connections

        except Exception as e:
            self.logger.error(f"Error extracting connections from {url}: {str(e)}")
            return []

    def _extract_connections_basic(self, text):
        """Basic extraction of symbol connections based on co-occurrence in sentences"""
        connections = []

        # Break into sentences
        sentences = sent_tokenize(text)

        for sentence in sentences:
            sentence = sentence.lower()

            # Find mentioned symbols in this sentence
            mentioned_symbols = []

            # Check both original names and aliases
            for name, symbol_id in self.symbol_map.items():
                if name in sentence:
                    mentioned_symbols.append((symbol_id, name))

            for alias, symbol_id in self.symbol_aliases.items():
                if alias in sentence and not any(id == symbol_id for id, _ in mentioned_symbols):
                    mentioned_symbols.append((symbol_id, alias))

            # Create connections between co-mentioned symbols
            if len(mentioned_symbols) >= 2:
                for (source_id, source_name), (target_id, target_name) in itertools.combinations(mentioned_symbols, 2):
                    # Make sure we're not connecting a symbol to itself (due to aliases)
                    if source_id != target_id:
                        # Extract a snippet describing the relationship
                        description = self._extract_relationship_description(
                            sentence, source_name, target_name)

                        connections.append({
                            'source': source_id,
                            'target': target_id,
                            'sentence': sentence,
                            'description': description,
                            'source_name': source_name,
                            'target_name': target_name
                        })

        return connections

    def _extract_connections_spacy(self, text):
        """Advanced extraction of symbol connections using spaCy NLP"""
        connections = []

        # Process the text with spaCy
        doc = nlp(text)

        # Analyze each sentence
        for sent in doc.sents:
            sentence = sent.text.lower()

            # Find mentioned symbols
            mentioned_symbols = []

            # Check both original names and aliases
            for name, symbol_id in self.symbol_map.items():
                if name in sentence:
                    mentioned_symbols.append((symbol_id, name))

            for alias, symbol_id in self.symbol_aliases.items():
                if alias in sentence and not any(id == symbol_id for id, _ in mentioned_symbols):
                    mentioned_symbols.append((symbol_id, alias))

            # Create connections between co-mentioned symbols
            if len(mentioned_symbols) >= 2:
                for (source_id, source_name), (target_id, target_name) in itertools.combinations(mentioned_symbols, 2):
                    # Make sure we're not connecting a symbol to itself (due to aliases)
                    if source_id != target_id:
                        # Check if there are relationship verbs between the symbols
                        relationship_strength = self._analyze_relationship_strength(
                            sent, source_name, target_name)

                        # Only add strong connections
                        if relationship_strength > 0.3:
                            # Extract a snippet describing the relationship
                            description = self._extract_relationship_description(
                                sentence, source_name, target_name)

                            connections.append({
                                'source': source_id,
                                'target': target_id,
                                'sentence': sentence,
                                'description': description,
                                'strength': relationship_strength,
                                'source_name': source_name,
                                'target_name': target_name
                            })

        return connections

    def _analyze_relationship_strength(self, spacy_sent, source_name, target_name):
        """Analyze the strength of relationship between two symbols in a sentence"""
        # Connection strength indicators
        relationship_verbs = {
            'strong': ['represents', 'symbolizes', 'embodies', 'signifies', 'connects',
                       'relates', 'corresponds', 'linked', 'associated', 'derived'],
            'medium': ['similar', 'like', 'compared', 'parallels', 'resembles', 'inspired',
                       'influenced', 'developed', 'evolved', 'transformed'],
            'weak': ['and', 'with', 'also', 'additionally', 'moreover', 'both', 'either']
        }

        # Convert to lowercase for matching
        text = spacy_sent.text.lower()

        # Base strength on proximity
        source_pos = text.find(source_name)
        target_pos = text.find(target_name)

        if source_pos == -1 or target_pos == -1:
            return 0

        # Calculate distance (normalized by sentence length)
        distance = abs(source_pos - target_pos) / len(text)
        proximity_score = 1 - min(distance, 1)  # Closer = stronger

        # Check for relationship verbs
        verb_score = 0
        for strength, verbs in relationship_verbs.items():
            for verb in verbs:
                if verb in text:
                    if strength == 'strong':
                        verb_score = 0.8
                        break
                    elif strength == 'medium':
                        verb_score = 0.5
                        break
                    else:  # weak
                        verb_score = 0.2
                        break
            if verb_score > 0:
                break

        # Check for dependency paths between symbols
        dep_score = 0
        try:
            source_tokens = [token for token in spacy_sent if source_name in token.text.lower()]
            target_tokens = [token for token in spacy_sent if target_name in token.text.lower()]

            if source_tokens and target_tokens:
                # Check if there's a direct dependency path
                for s_token in source_tokens:
                    for t_token in target_tokens:
                        if s_token.is_ancestor(t_token) or t_token.is_ancestor(s_token):
                            dep_score = 0.7
                            break
        except:
            # If dependency parsing fails, ignore this score
            pass

        # Calculate final strength (weighted average)
        final_strength = (proximity_score * 0.4) + (verb_score * 0.4) + (dep_score * 0.2)
        return min(round(final_strength, 2), 1.0)  # Cap at 1.0

    def _extract_relationship_description(self, sentence, source_name, target_name):
        """Extract a description of the relationship between symbols"""
        # Start with the full sentence
        description = sentence

        # Try to find a more focused description
        try:
            # Look for patterns like "[source] ... [relationship] ... [target]"
            source_pos = sentence.find(source_name)
            target_pos = sentence.find(target_name)

            if source_pos > -1 and target_pos > -1:
                # Get the text between the two symbols
                if source_pos < target_pos:
                    middle = sentence[source_pos + len(source_name):target_pos].strip()
                    if len(middle) > 3 and len(middle) < 100:
                        description = f"{source_name} {middle} {target_name}"
                else:
                    middle = sentence[target_pos + len(target_name):source_pos].strip()
                    if len(middle) > 3 and len(middle) < 100:
                        description = f"{target_name} {middle} {source_name}"
        except:
            # Fall back to full sentence
            pass

        return description

    def transform(self, data, url):
        """Transform raw connection data to match our Connection model"""
        self.logger.info(f"Transforming {len(data)} connections from {url}")

        transformed = []

        for item in data:
            if not item:
                continue

            # Generate a deterministic ID for the connection
            source_id = item['source']
            target_id = item['target']

            # Ensure consistent ordering (lower ID first)
            if source_id > target_id:
                source_id, target_id = target_id, source_id

            # Extract or calculate connection strength
            if 'strength' in item:
                strength = item['strength']
            else:
                # Calculate strength based on description quality
                desc_length = len(item['description'])
                if desc_length > 100:
                    strength = 0.8
                elif desc_length > 50:
                    strength = 0.6
                else:
                    strength = 0.4

            # Create the transformed connection
            connection = {
                'source': source_id,
                'target': target_id,
                'strength': strength,
                'description': self.clean_text(item['description']),
                'source_url': url,
                'date_added': datetime.datetime.now().strftime('%Y-%m-%d'),
            }

            # Add only if we have a good connection
            if self._validate_connection(connection):
                transformed.append(connection)

        self.logger.info(f"Transformed {len(transformed)} valid connections")
        return transformed

    def _validate_connection(self, connection):
        """Validate a connection before adding it to results"""
        # Check for duplicates
        for existing in self.results:
            if (existing['source'] == connection['source'] and
                    existing['target'] == connection['target']):
                # If we already have this connection, keep the one with better description
                if len(existing['description']) < len(connection['description']):
                    # Replace with better description
                    existing.update(connection)
                return False

        # Basic validation
        if not connection['description'] or len(connection['description']) < 10:
            return False

        return True
