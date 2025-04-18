class Connection:
    """Model representing a connection between symbols"""

    def __init__(self, source, target, strength, description):
        self.source = source
        self.target = target
        self.strength = strength
        self.description = description

    def to_dict(self):
        """Convert instance to dictionary"""
        return {
            'source': self.source,
            'target': self.target,
            'strength': self.strength,
            'description': self.description
        }