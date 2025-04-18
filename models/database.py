from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

# Association table for many-to-many relationships
symbol_element_association = db.Table('symbol_element',
                                      db.Column('symbol_id', db.Integer, db.ForeignKey('symbol.id'), primary_key=True),
                                      db.Column('element_id', db.Integer, db.ForeignKey('element.id'), primary_key=True)
                                      )


class Symbol(db.Model):
    """Model for occult symbols"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    tradition = db.Column(db.String(100), nullable=False, index=True)
    century_origin = db.Column(db.Integer, nullable=False, index=True)
    description = db.Column(db.Text)
    usage = db.Column(db.Text)
    visual_elements = db.Column(db.Text)  # Stored as JSON string

    # Relationships
    connections_as_source = db.relationship('Connection', foreign_keys='Connection.source_id', backref='source',
                                            lazy='dynamic')
    connections_as_target = db.relationship('Connection', foreign_keys='Connection.target_id', backref='target',
                                            lazy='dynamic')
    elements = db.relationship('Element', secondary=symbol_element_association,
                               backref=db.backref('symbols', lazy='dynamic'))

    def to_dict(self):
        """Convert instance to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'tradition': self.tradition,
            'element': ','.join([e.name for e in self.elements]),
            'century_origin': self.century_origin,
            'description': self.description,
            'usage': self.usage,
            'visual_elements': json.loads(self.visual_elements) if self.visual_elements else []
        }


class Connection(db.Model):
    """Model for connections between symbols"""
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey('symbol.id'), nullable=False)
    target_id = db.Column(db.Integer, db.ForeignKey('symbol.id'), nullable=False)
    strength = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)

    def to_dict(self):
        """Convert instance to dictionary"""
        return {
            'source': self.source_id,
            'target': self.target_id,
            'strength': self.strength,
            'description': self.description
        }


class Tradition(db.Model):
    """Model for esoteric traditions"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    start_century = db.Column(db.Integer, nullable=False)
    end_century = db.Column(db.Integer, nullable=False)
    region = db.Column(db.String(100), nullable=False)
    major_texts = db.Column(db.Text)  # Stored as JSON string
    key_figures = db.Column(db.Text)  # Stored as JSON string
    core_concepts = db.Column(db.Text)  # Stored as JSON string

    def to_dict(self):
        """Convert instance to dictionary"""
        return {
            'name': self.name,
            'start_century': self.start_century,
            'end_century': self.end_century,
            'region': self.region,
            'major_texts': json.loads(self.major_texts) if self.major_texts else [],
            'key_figures': json.loads(self.key_figures) if self.key_figures else [],
            'core_concepts': json.loads(self.core_concepts) if self.core_concepts else []
        }


class Element(db.Model):
    """Model for elemental associations"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    description = db.Column(db.Text)
    correspondences = db.Column(db.Text)  # Stored as JSON string

    def to_dict(self):
        """Convert instance to dictionary"""
        return {
            'element': self.name,
            'description': self.description,
            'count': self.symbols.count(),
            'correspondences': json.loads(self.correspondences) if self.correspondences else {},
            'symbols': [s.id for s in self.symbols],
            'traditions': list(set([s.tradition for s in self.symbols]))
        }


class TimePeriod(db.Model):
    """Model for time periods"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_year = db.Column(db.Integer, nullable=False)
    end_year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)

    def to_dict(self):
        """Convert instance to dictionary"""
        return {
            'name': self.name,
            'start_year': self.start_year,
            'end_year': self.end_year,
            'description': self.description
        }