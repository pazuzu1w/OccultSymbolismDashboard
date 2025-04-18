class Tradition:
    """Model representing an esoteric tradition"""

    def __init__(self, name, start_century, end_century, region, major_texts, key_figures=None, core_concepts=None):
        self.name = name
        self.start_century = start_century
        self.end_century = end_century
        self.region = region
        self.major_texts = major_texts
        self.key_figures = key_figures or []
        self.core_concepts = core_concepts or []

    def to_dict(self):
        """Convert instance to dictionary"""
        return {
            'name': self.name,
            'start_century': self.start_century,
            'end_century': self.end_century,
            'region': self.region,
            'major_texts': self.major_texts,
            'key_figures': self.key_figures,
            'core_concepts': self.core_concepts
        }