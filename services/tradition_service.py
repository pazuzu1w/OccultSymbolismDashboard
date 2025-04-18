class TraditionService:
    """Service for handling tradition-related operations"""

    def __init__(self, data_cache):
        self.data_cache = data_cache
        self.traditions = data_cache["raw_data"]["traditions"]
        self.symbols = data_cache["raw_data"]["symbols"]
        self.processed_data = data_cache["processed_data"]

    def get_all_traditions(self):
        """Return all traditions"""
        return self.traditions

    def get_tradition_by_name(self, name):
        """Get a single tradition by name"""
        for tradition in self.traditions:
            if tradition["name"].lower() == name.lower():
                return tradition
        return None

    def get_timeline_data(self):
        """Get prepared tradition timeline data"""
        return self.processed_data["tradition_timeline"]

    def get_transition_data(self):
        """Get tradition transition/influence data"""
        return self.processed_data["tradition_transitions"]

    def get_tradition_symbols(self, tradition_name):
        """Get all symbols associated with a specific tradition"""
        tradition_symbols = []

        for symbol in self.symbols:
            # Handle multi-tradition entries
            traditions = symbol["tradition"].split("/")
            if tradition_name in traditions:
                tradition_symbols.append(symbol)

        return tradition_symbols

    def get_core_concepts(self, tradition_name):
        """Get core concepts for a specific tradition"""
        tradition = self.get_tradition_by_name(tradition_name)
        if tradition:
            return tradition.get("core_concepts", [])
        return []

    def get_key_figures(self, tradition_name):
        """Get key figures for a specific tradition"""
        tradition = self.get_tradition_by_name(tradition_name)
        if tradition:
            return tradition.get("key_figures", [])
        return []