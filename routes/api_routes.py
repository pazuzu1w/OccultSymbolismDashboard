from flask import Blueprint, jsonify, request
from data.loader import DataLoader
from services.symbol_service import SymbolService
from services.tradition_service import TraditionService
from services.analysis_service import AnalysisService
from models.database import Symbol, Tradition, db

# Create Blueprint
bp = Blueprint('api', __name__)

# Remove this old initialization code
# data_cache = DataLoader.load_data()
# symbol_service = SymbolService(data_cache)
# tradition_service = TraditionService(data_cache)
# analysis_service = AnalysisService(data_cache)

# Replace with simple service initialization
symbol_service = SymbolService()
tradition_service = TraditionService()
analysis_service = AnalysisService()


# Symbol routes
@bp.route('/symbols')
def get_symbols():
    """Return all symbols as JSON"""
    return jsonify(symbol_service.get_all_symbols())


@bp.route('/symbols/<int:symbol_id>')
def get_symbol(symbol_id):
    """Return a specific symbol by ID"""
    symbol = symbol_service.get_symbol_by_id(symbol_id)
    if symbol:
        return jsonify(symbol)
    return jsonify({"error": "Symbol not found"}), 404


@bp.route('/symbols/<int:symbol_id>/connections')
def get_symbol_connections(symbol_id):
    """Return symbols connected to the specified symbol"""
    connected_symbols = symbol_service.get_connected_symbols(symbol_id)
    return jsonify(connected_symbols)


@bp.route('/connections')
def get_connections():
    """Return symbol connections for network graph"""
    return jsonify(symbol_service.get_connections())


@bp.route('/network')
def get_network_data():
    """Return prepared network data for visualization"""
    return jsonify(symbol_service.get_network_data())


@bp.route('/timeline')
def get_timeline():
    """Return symbol timeline data for visualization"""
    return jsonify(symbol_service.get_timeline_data())


@bp.route('/search')
def search_symbols():
    """Search symbols by name, tradition, element, or description"""
    query = request.args.get('q', '').lower()
    return jsonify(symbol_service.search(query))


# Tradition routes
@bp.route('/traditions')
def get_traditions():
    """Return all traditions"""
    return jsonify(tradition_service.get_all_traditions())


@bp.route('/traditions/<string:name>')
def get_tradition(name):
    """Return a specific tradition by name"""
    tradition = tradition_service.get_tradition_by_name(name)
    if tradition:
        return jsonify(tradition)
    return jsonify({"error": "Tradition not found"}), 404


@bp.route('/traditions/<string:name>/symbols')
def get_tradition_symbols(name):
    """Return symbols associated with a specific tradition"""
    tradition_symbols = tradition_service.get_tradition_symbols(name)
    return jsonify(tradition_symbols)


@bp.route('/tradition-timeline')
def get_tradition_timeline():
    """Return tradition timeline data"""
    return jsonify(tradition_service.get_timeline_data())


# Analysis routes
@bp.route('/element-distribution')
def get_element_distribution():
    """Return element distribution data"""
    return jsonify(analysis_service.get_element_distribution())


@bp.route('/elements/<string:name>')
def get_element(name):
    """Return details for a specific element"""
    element = analysis_service.get_element_by_name(name)
    if element:
        return jsonify(element)
    return jsonify({"error": "Element not found"}), 404


@bp.route('/tradition-frequency')
def get_tradition_frequency():
    """Return tradition frequency data"""
    return jsonify(analysis_service.get_tradition_symbol_frequency())


@bp.route('/geographic-distribution')
def get_geographic_distribution():
    """Return geographic distribution data"""
    return jsonify(analysis_service.get_geographic_distribution())


@bp.route('/dashboard/summary')
def get_dashboard_summary():
    """Return summarized data for dashboard overview"""
    # Count total symbols and traditions
    symbol_count = Symbol.query.count()
    tradition_count = Tradition.query.count()

    # Get timeline span
    earliest_symbol = Symbol.query.order_by(Symbol.century_origin).first()
    latest_symbol = Symbol.query.order_by(Symbol.century_origin.desc()).first()

    if earliest_symbol and latest_symbol:
        earliest_year = earliest_symbol.century_origin * 100 - 50
        latest_year = latest_symbol.century_origin * 100 - 50
    else:
        earliest_year = 0
        latest_year = 0

    # Get top traditions
    tradition_freq = analysis_service.get_tradition_symbol_frequency()
    top_traditions = tradition_freq[:5] if tradition_freq else []

    return jsonify({
        "total_symbols": symbol_count,
        "total_traditions": tradition_count,
        "time_span": {
            "earliest": earliest_year,
            "latest": latest_year,
            "range_years": latest_year - earliest_year
        },
        "top_traditions": top_traditions
    })