class AnalysisService:
    """Service for data analysis operations"""

    def __init__(self, data_cache):
        self.data_cache = data_cache
        self.symbols_df = data_cache["symbols_df"]
        self.traditions_df = data_cache["traditions_df"]
        self.processed_data = data_cache["processed_data"]

    def get_element_distribution(self):
        """Get element distribution data"""
        return self.processed_data["element_distribution"]

    def get_tradition_symbol_frequency(self):
        """Get tradition frequency data"""
        return self.processed_data["tradition_frequency"]

    def get_geographic_distribution(self):
        """Get geographic distribution data"""
        return self.processed_data["geographic_distribution"]

    def get_symbol_categories(self):
        """Get symbol category data"""
        return self.processed_data["symbol_categories"]

    def get_regional_influence(self):
        """Get regional influence data"""
        return self.processed_data["regional_influence"]

    def get_element_by_name(self, element_name):
        """Get details for a specific element"""
        for element in self.processed_data["element_distribution"]:
            if element["element"].lower() == element_name.lower():
                return element
        return None