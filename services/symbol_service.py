from models.database import Symbol, Connection, db


class SymbolService:
    """Service for handling symbol-related operations"""

    def get_all_symbols(self):
        """Return all symbols"""
        symbols = Symbol.query.all()
        return [symbol.to_dict() for symbol in symbols]

    def get_symbol_by_id(self, symbol_id):
        """Get a single symbol by ID"""
        symbol = Symbol.query.get(symbol_id)
        return symbol.to_dict() if symbol else None


    def get_connections(self):
        """Return all symbol connections"""
        connections = Connection.query.all()
        return [connection.to_dict() for connection in connections]

    def get_network_data(self):
        """Get prepared network visualization data"""
        # Get all symbols and connections
        symbols = Symbol.query.all()
        connections = Connection.query.all()

        # Create color mapping
        traditions = set()
        for symbol in symbols:
            for tradition in symbol.tradition.split('/'):
                traditions.add(tradition.strip())

        # Create a color scale for traditions
        import random
        from colorsys import hsv_to_rgb

        def random_color():
            h = random.random()
            s = 0.7 + random.random() * 0.3  # 0.7-1.0
            v = 0.6 + random.random() * 0.3  # 0.6-0.9
            r, g, b = hsv_to_rgb(h, s, v)
            return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"

        color_map = {tradition: random_color() for tradition in traditions}

        # Prepare nodes
        nodes = []
        for symbol in symbols:
            # Get primary tradition
            primary_tradition = symbol.tradition.split('/')[0].strip()

            node = {
                "id": symbol.id,
                "name": symbol.name,
                "tradition": symbol.tradition,
                "element": ','.join([e.name for e in symbol.elements]),
                "century": symbol.century_origin,
                "color": color_map.get(primary_tradition, "#888888"),
                "description": symbol.description
            }
            nodes.append(node)

        # Prepare links
        links = [connection.to_dict() for connection in connections]

        return {
            "nodes": nodes,
            "links": links
        }

    def get_timeline_data(self):
        """Get prepared timeline visualization data"""
        symbols = Symbol.query.all()
        timeline_data = []

        for symbol in symbols:
            century = symbol.century_origin
            year = century * 100 - 50  # Approximate middle of century

            if century <= 0:
                year_display = f"{abs(year)} BCE"
            else:
                year_display = f"{year} CE"

            timeline_data.append({
                "id": symbol.id,
                "name": symbol.name,
                "tradition": symbol.tradition,
                "element": ','.join([e.name for e in symbol.elements]),
                "year": year,
                "year_display": year_display,
                "description": symbol.description
            })

        # Sort by year
        timeline_data = sorted(timeline_data, key=lambda x: x["year"])
        return timeline_data

    def get_connected_symbols(self, symbol_id):
        """Get all symbols directly connected to the specified symbol"""
        # Get the symbol
        symbol = Symbol.query.get(symbol_id)
        if not symbol:
            return []

        # Get connections where this symbol is source or target
        connected_ids = set()

        # As source
        source_connections = Connection.query.filter_by(source_id=symbol_id).all()
        for conn in source_connections:
            connected_ids.add(conn.target_id)

        # As target
        target_connections = Connection.query.filter_by(target_id=symbol_id).all()
        for conn in target_connections:
            connected_ids.add(conn.source_id)

        # Get the symbol data for each connected ID
        connected_symbols = []
        for conn_id in connected_ids:
            connected_symbol = Symbol.query.get(conn_id)
            if connected_symbol:
                connected_symbols.append(connected_symbol.to_dict())

        return connected_symbols

    def search(self, query):
        """Search symbols by name, tradition, element, or description"""
        if not query:
            return []

        query = f"%{query.lower()}%"

        # Search in symbols
        symbols = Symbol.query.filter(
            db.or_(
                db.func.lower(Symbol.name).like(query),
                db.func.lower(Symbol.tradition).like(query),
                db.func.lower(Symbol.description).like(query)
            )
        ).all()

        # Also search in elements
        element_symbols = []
        from models.database import Element
        elements = Element.query.filter(db.func.lower(Element.name).like(query)).all()
        for element in elements:
            for symbol in element.symbols:
                if symbol not in symbols:
                    element_symbols.append(symbol)

        # Combine results
        all_symbols = symbols + element_symbols

        return [symbol.to_dict() for symbol in all_symbols]