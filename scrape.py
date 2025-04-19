# scrape.py
import argparse
import json
import logging
import os
import sys
from datetime import datetime
from scrapers.manager import ScraperManager
from data.scraper_integration import ScraperIntegration


def setup_logging(log_level, log_file=None):
    """Set up logging configuration"""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO

    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    if log_file:
        logging.basicConfig(
            level=numeric_level,
            format=log_format,
            filename=log_file,
            filemode='a'
        )
        # Also log to console
        console = logging.StreamHandler()
        console.setLevel(numeric_level)
        console.setFormatter(logging.Formatter(log_format))
        logging.getLogger('').addHandler(console)
    else:
        logging.basicConfig(
            level=numeric_level,
            format=log_format
        )

    # Suppress noisy loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('chardet').setLevel(logging.WARNING)


def load_sources_config(config_file):
    """Load sources configuration from a JSON file"""
    if not os.path.exists(config_file):
        logging.error(f"Config file not found: {config_file}")
        return None

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config
    except Exception as e:
        logging.error(f"Error loading config file: {str(e)}")
        return None


def get_default_sources():
    """Return a default sources configuration"""
    return [
        {
            "type": "symbol",
            "urls": [
                "https://en.wikipedia.org/wiki/Esoteric_symbols",
                "https://en.wikipedia.org/wiki/Alchemical_symbol",
                "https://en.wikipedia.org/wiki/Sigil_(magic)",
                "https://en.wikipedia.org/wiki/Pentagram",
                "https://en.wikipedia.org/wiki/Ankh",
                "https://www.sacred-texts.com/sym/index.htm"
            ]
        },
        {
            "type": "tradition",
            "urls": [
                "https://en.wikipedia.org/wiki/Western_esotericism",
                "https://en.wikipedia.org/wiki/Hermeticism",
                "https://en.wikipedia.org/wiki/Alchemy",
                "https://en.wikipedia.org/wiki/Kabbalah",
                "https://en.wikipedia.org/wiki/Ceremonial_magic",
                "https://www.sacred-texts.com/eso/index.htm"
            ]
        }
    ]


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Occult Symbolism Web Scraper')

    parser.add_argument('--config', '-c', default=None,
                        help='Path to sources configuration file')
    parser.add_argument('--input', '-i', default=None,
                        help='Path to existing data file to update')
    parser.add_argument('--output', '-o', default='data/scraped_data.json',
                        help='Path to output file')
    parser.add_argument('--log-level', '-l', default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        help='Logging level')
    parser.add_argument('--log-file', '-f', default=None,
                        help='Log file path')
    parser.add_argument('--max-workers', '-w', type=int, default=4,
                        help='Maximum number of parallel scrapers')
    parser.add_argument('--standalone', '-s', action='store_true',
                        help='Run in standalone mode without merging with existing data')

    args = parser.parse_args()

    # Set up logging
    setup_logging(args.log_level, args.log_file)

    # Create a unique run ID
    run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    logging.info(f"Starting scraper run {run_id}")

    # Load sources configuration
    if args.config:
        sources = load_sources_config(args.config)
        if not sources:
            sources = get_default_sources()
            logging.warning("Using default sources configuration")
    else:
        sources = get_default_sources()
        logging.info("Using default sources configuration")

    # Initialize the integration
    integration = None
    if not args.standalone and args.input:
        if args.input.endswith('.py'):
            # Handle Python module specially
            try:
                import importlib.util
                import sys

                # Add the directory to sys.path
                sys.path.append(os.path.dirname(os.path.abspath(args.input)))

                # Import the module
                module_name = os.path.basename(args.input).replace('.py', '')
                spec = importlib.util.spec_from_file_location(module_name, args.input)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Get data from the module
                existing_data = module.get_complete_dataset()

                # Create integration with this data
                integration = ScraperIntegration(existing_data=existing_data)
            except Exception as e:
                logging.error(f"Error importing Python dataset: {str(e)}", exc_info=True)
                return 1
        else:
            # Regular file handling
            integration = ScraperIntegration(data_file=args.input)

    try:
        if args.standalone:
            # Run in standalone mode
            logging.info("Running in standalone mode")
            manager = ScraperManager(max_workers=args.max_workers)
            manager.add_sources(sources)

            results = manager.run_all()

            # Save results directly
            output_dir = os.path.dirname(args.output)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump({
                    'symbols': results['symbols'],
                    'traditions': results['traditions'],
                    'connections': results['connections'],
                    'metadata': {
                        'scrape_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'run_id': run_id,
                        'total_symbols': len(results['symbols']),
                        'total_traditions': len(results['traditions']),
                        'total_connections': len(results['connections'])
                    }
                }, f, indent=2, ensure_ascii=False)

            logging.info(f"Results saved to {args.output}")
        else:
            # Run with integration
            logging.info("Running with data integration")

            if not integration:
                integration = ScraperIntegration()

            integration.run_scraper(sources, args.output)

        logging.info(f"Scraper run {run_id} completed successfully")
        return 0

    except Exception as e:
        logging.error(f"Error in scraper run {run_id}: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())


"""Run the basic scraper:
python scrape.py --output data/scraped_data.json

Run with a custom configuration:
python scrape.py --config sources_config.json --output data/custom_scrape.json

Merge with existing data:
python scrape.py --input data/occult_symbols_dataset.py --output data/updated_dataset.json

merge with existing db
python -m flask db upgrade
"""