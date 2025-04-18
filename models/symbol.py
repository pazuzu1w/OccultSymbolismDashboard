class Symbol:
    """Model representing an occult symbol"""

    def __init__(self, id, name, tradition, element, century_origin, description=None, usage=None,
                 visual_elements=None):
        self.id = id
        self.name = name
        self.tradition = tradition
        self.element = element
        self.century_origin = century_origin
        self.description = description
        self.usage = usage
        self.visual_elements = visual_elements or []

    def to_dict(self):
        """Convert instance to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'tradition': self.tradition,
            'element': self.element,
            'century_origin': self.century_origin,
            'description': self.description,
            'usage': self.usage,
            'visual_elements': self.visual_elements
        }