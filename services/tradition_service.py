from models.database import Tradition, Symbol, db
import json
from models.database import Tradition, Symbol, db

class TraditionService:
    """Service for handling tradition-related operations"""

    def get_all_traditions(self):
        """Return all traditions"""
        traditions = Tradition.query.all()
        return [tradition.to_dict() for tradition in traditions]

    def get_tradition_by_name(self, name):
        """Get a single tradition by name"""
        tradition = Tradition.query.filter(db.func.lower(Tradition.name) == name.lower()).first()
        return tradition.to_dict() if tradition else None

    def get_timeline_data(self):
        """Get prepared tradition timeline data"""
        traditions = Tradition.query.all()
        traditions_timeline = []

        for tradition in traditions:
            # Convert century notation to years
            start_year = tradition.start_century * 100
            end_year = tradition.end_century * 100

            # If end_century is 21, set it to current year
            if tradition.end_century == 21:
                end_year = 2025

            tradition_data = {
                "name": tradition.name,
                "start_year": start_year,
                "end_year": end_year,
                "duration": end_year - start_year,
                "midpoint": start_year + ((end_year - start_year) / 2),
                "region": tradition.region,
                "major_texts": json.loads(tradition.major_texts) if tradition.major_texts else [],
                "key_figures": json.loads(tradition.key_figures) if tradition.key_figures else [],
                "core_concepts": json.loads(tradition.core_concepts) if tradition.core_concepts else []
            }

            traditions_timeline.append(tradition_data)

        # Sort by start_year
        traditions_timeline = sorted(traditions_timeline, key=lambda x: x["start_year"])
        return traditions_timeline

    def get_tradition_symbols(self, tradition_name):
        """Get all symbols associated with a specific tradition"""
        # Handle multi-tradition symbols by using LIKE query
        symbols = Symbol.query.filter(
            db.or_(
                Symbol.tradition == tradition_name,
                Symbol.tradition.like(f"{tradition_name}/%"),
                Symbol.tradition.like(f"%/{tradition_name}"),
                Symbol.tradition.like(f"%/{tradition_name}/%")
            )
        ).all()

        return [symbol.to_dict() for symbol in symbols]

    def get_core_concepts(self, tradition_name):
        """Get core concepts for a specific tradition"""
        tradition = Tradition.query.filter(db.func.lower(Tradition.name) == tradition_name.lower()).first()
        if tradition and tradition.core_concepts:
            return json.loads(tradition.core_concepts)
        return []

    def get_key_figures(self, tradition_name):
        """Get key figures for a specific tradition"""
        tradition = Tradition.query.filter(db.func.lower(Tradition.name) == tradition_name.lower()).first()
        if tradition and tradition.key_figures:
            return json.loads(tradition.key_figures)
        return []