class SymbolService:
    """Service for handling symbol-related operations"""

    def __init__(self, data_cache):
        self.data_cache = data_cache
        self.symbols_df = data_cache["symbols_df"]
        self.symbols = data_cache["raw_data"]["symbols"]
        self.connections = data_cache["raw_data"]["connections"]
        self.processed_data = data_cache["processed_data"]

    def get_all_symbols(self):
        """Return all symbols"""
        return self.symbols

    def get_symbol_by_id(self, symbol_id):
        """Get a single symbol by ID"""
        for symbol in self.symbols:
            if symbol["id"] == symbol_id:
                return symbol
        return None

    def get_connections(self):
        """Return all symbol connections"""
        return self.connections

    def get_network_data(self):
        """Get prepared network visualization data"""
        return self.processed_data["network_graph"]

    def get_timeline_data(self):
        """Get prepared timeline visualization data"""
        return self.processed_data["symbol_timeline"]

    def get_connected_symbols(self, symbol_id):
        """Get all symbols directly connected to the specified symbol"""
        connected_ids = []

        # Find all connections for this symbol
        for connection in self.connections:
            if connection["source"] == symbol_id:
                connected_ids.append(connection["target"])
            elif connection["target"] == symbol_id:
                connected_ids.append(connection["source"])

        # Get the actual symbol data
        connected_symbols = []
        for connected_id in connected_ids:
            symbol = self.get_symbol_by_id(connected_id)
            if symbol:
                connected_symbols.append(symbol)

        return connected_symbols

    def search(self, query):
        """Search symbols by name, tradition, element, or description"""
        if not query:
            return []

        query = query.lower()
        results = []

        for symbol in self.symbols:
            if (query in symbol["name"].lower() or
                    query in symbol["tradition"].lower() or
                    query in symbol["element"].lower() or
                    (symbol.get("description") and query in symbol["description"].lower())):
                results.append(symbol)

        return results