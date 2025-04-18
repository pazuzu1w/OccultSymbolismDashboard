import json
from models.database import Element, Symbol, Tradition, db


class AnalysisService:
    """Service for data analysis operations"""

    def get_element_distribution(self):
        """Get element distribution data"""
        elements = Element.query.all()

        element_details = []
        for element in elements:
            element_details.append({
                "element": element.name,
                "count": element.symbols.count(),
                "description": element.description,
                "symbols": [s.id for s in element.symbols],
                "traditions": list(set([s.tradition for s in element.symbols])),
                "correspondences": json.loads(element.correspondences) if element.correspondences else {}
            })

        return element_details

    def get_tradition_symbol_frequency(self):
        """Get tradition frequency data"""
        # Get all symbols
        symbols = Symbol.query.all()

        # Count by tradition
        tradition_counts = {}
        for symbol in symbols:
            # Handle multi-tradition entries
            traditions = symbol.tradition.split('/')
            for tradition in traditions:
                tradition = tradition.strip()
                if tradition in tradition_counts:
                    tradition_counts[tradition] += 1
                else:
                    tradition_counts[tradition] = 1

        # Convert to list format
        result = [{"tradition": k, "count": v} for k, v in tradition_counts.items()]

        # Sort by count
        result.sort(key=lambda x: x["count"], reverse=True)

        return result

    def get_geographic_distribution(self):
        """Get geographic distribution data"""
        # Get all traditions
        traditions = Tradition.query.all()

        # Count by region
        regions = {}
        for tradition in traditions:
            region = tradition.region
            # Handle multi-region entries
            if '/' in region:
                for r in region.split('/'):
                    r = r.strip()
                    if r in regions:
                        regions[r] += 1
                    else:
                        regions[r] = 1
            else:
                if region in regions:
                    regions[region] += 1
                else:
                    regions[region] = 1

        # Convert to list format
        result = [{"region": k, "count": v} for k, v in regions.items()]

        # Sort by count
        result.sort(key=lambda x: x["count"], reverse=True)

        return result

    def get_element_by_name(self, element_name):
        """Get details for a specific element"""
        element = Element.query.filter(db.func.lower(Element.name) == element_name.lower()).first()
        if element:
            return {
                "element": element.name,
                "count": element.symbols.count(),
                "description": element.description,
                "symbols": [s.id for s in element.symbols],
                "traditions": list(set([s.tradition for s in element.symbols])),
                "correspondences": json.loads(element.correspondences) if element.correspondences else {}
            }
        return None