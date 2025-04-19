# data/scraper_integration.py
import json
import os
import logging
from datetime import datetime
from scrapers.manager import ScraperManager


class ScraperIntegration:
    """Integrates scraped data with existing data structures"""

    # Modified version of the initialization in data/scraper_integration.py
    def __init__(self, existing_data=None, data_file=None):
        """Initialize with either existing data or data file path"""
        self.logger = logging.getLogger('ScraperIntegration')

        if existing_data:
            self.existing_data = existing_data
        elif data_file and os.path.exists(data_file):
            # Check if it's a Python file
            if data_file.endswith('.py'):
                try:
                    # Import the Python module and get the complete dataset
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("dataset_module", data_file)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Assuming the module has a function get_complete_dataset() as in your code
                    self.existing_data = module.get_complete_dataset()
                except Exception as e:
                    self.logger.error(f"Error importing Python dataset: {str(e)}")
                    self.existing_data = self._create_empty_dataset()
            else:
                # Try to load as JSON
                try:
                    with open(data_file, 'r', encoding='utf-8') as f:
                        self.existing_data = json.load(f)
                except json.JSONDecodeError:
                    self.logger.error(f"Error: {data_file} is not a valid JSON file")
                    self.existing_data = self._create_empty_dataset()
        else:
            self.existing_data = self._create_empty_dataset()

        # Check for minimal structure
        for key in ['symbols', 'connections', 'traditions']:
            if key not in self.existing_data:
                self.existing_data[key] = []

        # Create ID maps for faster lookups
        self.symbol_id_map = {s['id']: s for s in self.existing_data['symbols']}
        self.tradition_name_map = {t['name'].lower(): t for t in self.existing_data['traditions']}

        # Results after merging
        self.merged_data = None

    def _create_empty_dataset(self):
        """Create an empty dataset with the minimal structure"""
        return {
            'symbols': [],
            'connections': [],
            'traditions': [],
            'elements': [],
            'time_periods': []
        }

    def run_scraper(self, sources_config, output_file=None):
        """Run scraper with the given sources and merge results"""
        self.logger.info("Starting scraper run")

        # Initialize the scraper manager with existing data
        manager = ScraperManager(existing_data=self.existing_data)

        # Add sources to scrape
        manager.add_sources(sources_config)

        # Run all scrapers
        scraped_data = manager.run_all()

        # Merge with existing data
        self.merged_data = self.merge_data(scraped_data)

        # Save results if requested
        if output_file:
            self.save_merged_data(output_file)

        return self.merged_data

    def merge_data(self, scraped_data):
        """Merge scraped data with existing data"""
        self.logger.info(f"Merging scraped data ({len(scraped_data['symbols'])} symbols, "
                         f"{len(scraped_data['traditions'])} traditions, "
                         f"{len(scraped_data['connections'])} connections) with existing data")

        result = {k: list(v) for k, v in self.existing_data.items()}

        # Add a merge log for tracking
        result['merge_log'] = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'symbols_added': 0,
            'symbols_updated': 0,
            'traditions_added': 0,
            'traditions_updated': 0,
            'connections_added': 0,
            'connections_updated': 0
        }

        # Merge symbols
        for symbol in scraped_data['symbols']:
            # Check if this symbol exists by ID
            if symbol['id'] in self.symbol_id_map:
                existing = self.symbol_id_map[symbol['id']]
                updated = self._update_symbol(existing, symbol)
                if updated:
                    result['merge_log']['symbols_updated'] += 1
            else:
                # Check if we have a symbol with the same name
                name_match = None
                name_lower = symbol['name'].lower()

                for existing in self.existing_data['symbols']:
                    if existing['name'].lower() == name_lower:
                        name_match = existing
                        break

                if name_match:
                    # Update the existing symbol
                    updated = self._update_symbol(name_match, symbol)
                    if updated:
                        result['merge_log']['symbols_updated'] += 1
                else:
                    # New symbol
                    result['symbols'].append(symbol)
                    self.symbol_id_map[symbol['id']] = symbol
                    result['merge_log']['symbols_added'] += 1

        # Merge traditions
        for tradition in scraped_data['traditions']:
            name_lower = tradition['name'].lower()

            if name_lower in self.tradition_name_map:
                # Update existing tradition
                existing = self.tradition_name_map[name_lower]
                updated = self._update_tradition(existing, tradition)
                if updated:
                    result['merge_log']['traditions_updated'] += 1
            else:
                # New tradition
                result['traditions'].append(tradition)
                self.tradition_name_map[name_lower] = tradition
                result['merge_log']['traditions_added'] += 1

        # Merge connections
        for connection in scraped_data['connections']:
            # Check if this connection exists
            connection_exists = False

            for existing in self.existing_data['connections']:
                if (existing['source'] == connection['source'] and
                        existing['target'] == connection['target']):
                    connection_exists = True
                    # Update description if the new one is better
                    if len(connection['description']) > len(existing['description']):
                        existing['description'] = connection['description']
                        result['merge_log']['connections_updated'] += 1
                    break

            if not connection_exists:
                # New connection
                result['connections'].append(connection)
                result['merge_log']['connections_added'] += 1

        self.logger.info(f"Merge complete: Added {result['merge_log']['symbols_added']} symbols, "
                         f"{result['merge_log']['traditions_added']} traditions, "
                         f"{result['merge_log']['connections_added']} connections")

        return result

    def _update_symbol(self, existing, new):
        """Update an existing symbol with new data where appropriate"""
        updated = False

        # Fields that should be updated if the new value is better
        for field in ['description', 'usage', 'visual_elements']:
            if field in new and new[field] and (
                    field not in existing or len(str(new[field])) > len(str(existing.get(field, '')))):
                existing[field] = new[field]
                updated = True

        # Tradition: If existing is "Unknown" but new has a value
        if 'tradition' in new and new['tradition'] and (
                existing.get('tradition') == 'Unknown' or not existing.get('tradition')):
            existing['tradition'] = new['tradition']
            updated = True

        # Element: If existing is "Unknown" but new has a value
        if 'element' in new and new['element'] and (
                existing.get('element') == 'Unknown' or not existing.get('element')):
            existing['element'] = new['element']
            updated = True

        # Century: If existing is 0 but new has a value
        if 'century_origin' in new and new['century_origin'] and existing.get('century_origin', 0) == 0:
            existing['century_origin'] = new['century_origin']
            updated = True

        # Add source_url if missing
        if 'source_url' in new and new['source_url'] and 'source_url' not in existing:
            existing['source_url'] = new['source_url']
            updated = True

        # Set last_updated if changed
        if updated:
            existing['last_updated'] = datetime.now().strftime('%Y-%m-%d')

        return updated

    def _update_tradition(self, existing, new):
        """Update an existing tradition with new data where appropriate"""
        updated = False

        # Update fields if new has better data
        # Description: If new is longer
        if 'description' in new and new['description'] and (
                'description' not in existing or
                len(new['description']) > len(existing.get('description', ''))
        ):
            existing['description'] = new['description']
            updated = True

        # Region: If existing is Unknown but new has a value
        if 'region' in new and new['region'] and (
                'region' not in existing or
                existing['region'] == 'Unknown'
        ):
            existing['region'] = new['region']
            updated = True

        # Core concepts: Add any new ones
        if 'core_concepts' in new and new['core_concepts']:
            if 'core_concepts' not in existing:
                existing['core_concepts'] = []

            new_concepts = []
            existing_concepts_lower = [c.lower() for c in existing['core_concepts']]

            for concept in new['core_concepts']:
                if concept.lower() not in existing_concepts_lower:
                    new_concepts.append(concept)

            if new_concepts:
                existing['core_concepts'].extend(new_concepts)
                updated = True

        # Major texts: Add any new ones
        if 'major_texts' in new and new['major_texts']:
            if 'major_texts' not in existing:
                existing['major_texts'] = []

            new_texts = []
            existing_texts_lower = [t.lower() for t in existing['major_texts']]

            for text in new['major_texts']:
                if text.lower() not in existing_texts_lower and text != 'Unknown':
                    new_texts.append(text)

            if new_texts:
                existing['major_texts'].extend(new_texts)
                updated = True

        # Key figures: Add any new ones
        if 'key_figures' in new and new['key_figures']:
            if 'key_figures' not in existing:
                existing['key_figures'] = []

            new_figures = []
            existing_figures_lower = [f.lower() for f in existing['key_figures']]

            for figure in new['key_figures']:
                if figure.lower() not in existing_figures_lower:
                    new_figures.append(figure)

            if new_figures:
                existing['key_figures'].extend(new_figures)
                updated = True

        # Set last_updated if changed
        if updated:
            existing['last_updated'] = datetime.now().strftime('%Y-%m-%d')

        return updated

    def save_merged_data(self, output_file):
        """Save the merged data to a file"""
        if not self.merged_data:
            self.logger.warning("No merged data to save")
            return False

        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.merged_data, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Merged data saved to {output_file}")
        return True