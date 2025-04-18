from app import create_app
from models.database import db, Symbol, Connection, Tradition, Element, TimePeriod
import json
from data.occult_symbols_dataset import get_complete_dataset


def initialize_database():
    """Initialize database with occult symbols dataset"""
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()

        # Check if database is already populated
        if Symbol.query.count() > 0:
            print("Database already contains data. Skipping initialization.")
            return

        # Load data from dataset
        dataset = get_complete_dataset()

        # Create elements first
        elements = {}
        for element_data in dataset["elements"]:
            element = Element(
                name=element_data["name"],
                description=element_data["description"],
                correspondences=json.dumps(element_data.get("correspondences", {}))
            )
            db.session.add(element)
            # Store in dictionary for later reference
            elements[element_data["name"]] = element

        # Initial commit to get IDs
        db.session.commit()

        # Insert symbols
        symbols = {}
        for symbol_data in dataset["symbols"]:
            # Handle multi-element symbols
            element_names = symbol_data["element"].split('/')
            primary_element = element_names[0].strip()

            symbol = Symbol(
                id=symbol_data["id"],
                name=symbol_data["name"],
                tradition=symbol_data["tradition"],
                century_origin=symbol_data["century_origin"],
                description=symbol_data.get("description", ""),
                usage=symbol_data.get("usage", ""),
                visual_elements=json.dumps(symbol_data.get("visual_elements", []))
            )

            # Add element associations
            for element_name in element_names:
                element_name = element_name.strip()
                if element_name in elements:
                    symbol.elements.append(elements[element_name])

            db.session.add(symbol)
            symbols[symbol_data["id"]] = symbol

        # Commit to get symbol IDs
        db.session.commit()

        # Insert connections
        for conn_data in dataset["connections"]:
            connection = Connection(
                source_id=conn_data["source"],
                target_id=conn_data["target"],
                strength=conn_data["strength"],
                description=conn_data["description"]
            )
            db.session.add(connection)

        # Insert traditions
        for i, trad_data in enumerate(dataset["traditions"], 1):
            tradition = Tradition(
                id=i,
                name=trad_data["name"],
                start_century=trad_data["start_century"],
                end_century=trad_data["end_century"],
                region=trad_data["region"],
                major_texts=json.dumps(trad_data["major_texts"]),
                key_figures=json.dumps(trad_data.get("key_figures", [])),
                core_concepts=json.dumps(trad_data.get("core_concepts", []))
            )
            db.session.add(tradition)

        # Insert time periods
        for period_data in dataset["time_periods"]:
            # Convert century-based dates to years
            if 'symbols' in period_data:
                symbols_json = json.dumps(period_data["symbols"])
            else:
                symbols_json = "[]"

            period = TimePeriod(
                name=period_data["name"],
                start_year=period_data.get("start_year", 0),
                end_year=period_data.get("end_year", 0),
                description=period_data.get("description", "")
            )
            db.session.add(period)

        # Commit all changes
        db.session.commit()
        print("Database successfully initialized with occult symbols data.")


if __name__ == "__main__":
    initialize_database()