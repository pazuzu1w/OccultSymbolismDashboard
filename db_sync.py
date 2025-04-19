# db_sync.py - Script to synchronize JSON data with SQLAlchemy database

import json
import os
import logging
from datetime import datetime
from app import create_app
from models.database import db, Symbol, Tradition, Element, Connection, TimePeriod

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('db_sync')


def synchronize_db_with_json(json_file):
    """Synchronize the database with the contents of a JSON file"""
    if not os.path.exists(json_file):
        logger.error(f"JSON file not found: {json_file}")
        return False

    logger.info(f"Loading data from {json_file}")
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from {json_file}")
        return False

    app = create_app()
    with app.app_context():
        # Initialize counters for logging
        symbols_added = 0
        symbols_updated = 0
        traditions_added = 0
        traditions_updated = 0
        connections_added = 0

        # Synchronize symbols
        logger.info(f"Synchronizing {len(data.get('symbols', []))} symbols")
        for symbol_data in data.get('symbols', []):
            # Check if symbol exists
            symbol = Symbol.query.get(symbol_data.get('id'))

            if symbol:
                # Update existing symbol
                updated = False
                for field in ['name', 'tradition', 'description', 'usage']:
                    if field in symbol_data and getattr(symbol, field) != symbol_data[field]:
                        setattr(symbol, field, symbol_data[field])
                        updated = True

                # Handle visual_elements (JSON field)
                if 'visual_elements' in symbol_data:
                    visual_elements_json = json.dumps(symbol_data['visual_elements'])
                    if symbol.visual_elements != visual_elements_json:
                        symbol.visual_elements = visual_elements_json
                        updated = True

                # Handle century_origin
                if 'century_origin' in symbol_data and symbol.century_origin != symbol_data['century_origin']:
                    symbol.century_origin = symbol_data['century_origin']
                    updated = True

                if updated:
                    symbols_updated += 1
            else:
                # Create new symbol
                try:
                    new_symbol = Symbol(
                        id=symbol_data.get('id'),
                        name=symbol_data.get('name', ''),
                        tradition=symbol_data.get('tradition', ''),
                        century_origin=symbol_data.get('century_origin', 0),
                        description=symbol_data.get('description', ''),
                        usage=symbol_data.get('usage', ''),
                        visual_elements=json.dumps(symbol_data.get('visual_elements', []))
                    )
                    db.session.add(new_symbol)
                    symbols_added += 1
                except Exception as e:
                    logger.error(f"Error adding symbol {symbol_data.get('id')}: {str(e)}")

        # Synchronize traditions
        logger.info(f"Synchronizing {len(data.get('traditions', []))} traditions")
        for tradition_data in data.get('traditions', []):
            name = tradition_data.get('name')
            tradition = Tradition.query.filter_by(name=name).first()

            if tradition:
                # Update existing tradition
                updated = False

                # Update basic fields
                for field in ['start_century', 'end_century', 'region']:
                    if field in tradition_data and getattr(tradition, field) != tradition_data[field]:
                        setattr(tradition, field, tradition_data[field])
                        updated = True

                # Handle JSON fields
                for field in ['major_texts', 'key_figures', 'core_concepts']:
                    if field in tradition_data:
                        field_json = json.dumps(tradition_data[field])
                        if getattr(tradition, field) != field_json:
                            setattr(tradition, field, field_json)
                            updated = True

                if updated:
                    traditions_updated += 1
            else:
                # Create new tradition
                try:
                    new_tradition = Tradition(
                        name=name,
                        start_century=tradition_data.get('start_century', 0),
                        end_century=tradition_data.get('end_century', 0),
                        region=tradition_data.get('region', ''),
                        major_texts=json.dumps(tradition_data.get('major_texts', [])),
                        key_figures=json.dumps(tradition_data.get('key_figures', [])),
                        core_concepts=json.dumps(tradition_data.get('core_concepts', []))
                    )
                    db.session.add(new_tradition)
                    traditions_added += 1
                except Exception as e:
                    logger.error(f"Error adding tradition {name}: {str(e)}")

        # Synchronize connections
        logger.info(f"Synchronizing {len(data.get('connections', []))} connections")
        for conn_data in data.get('connections', []):
            source_id = conn_data.get('source')
            target_id = conn_data.get('target')

            # Check if connection exists
            connection = Connection.query.filter_by(
                source_id=source_id,
                target_id=target_id
            ).first()

            if not connection:
                try:
                    new_connection = Connection(
                        source_id=source_id,
                        target_id=target_id,
                        strength=conn_data.get('strength', 0.5),
                        description=conn_data.get('description', '')
                    )
                    db.session.add(new_connection)
                    connections_added += 1
                except Exception as e:
                    logger.error(f"Error adding connection {source_id}->{target_id}: {str(e)}")

        # Commit all changes
        try:
            db.session.commit()
            logger.info(f"Database synchronized successfully: "
                        f"Added {symbols_added} symbols, {traditions_added} traditions, "
                        f"{connections_added} connections; "
                        f"Updated {symbols_updated} symbols, {traditions_updated} traditions")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error committing changes to database: {str(e)}")
            return False


if __name__ == "__main__":
    # Specify the JSON file path
    json_file = 'data/updated_dataset.json'  # Adjust this to your file path

    # Run the synchronization
    success = synchronize_db_with_json(json_file)

    if success:
        print("Database successfully synchronized with JSON data")
    else:
        print("Database synchronization failed - check the logs for details")