from flask import Blueprint, jsonify, request
from data.loader import DataLoader
from services.symbol_service import SymbolService
from services.tradition_service import TraditionService
from services.analysis_service import AnalysisService

# Create Blueprint
bp = Blueprint('api', __name__)

# Initialize services
data_cache = DataLoader.load_data()
symbol_service = SymbolService(data_cache)
tradition_service = TraditionService(data_cache)
analysis_service = AnalysisService(data_cache)


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
    symbols = symbol_service.get_all_symbols()
    traditions = tradition_service.get_all_traditions()

    # Calculate time span
    timeline_data = symbol_service.get_timeline_data()
    earliest = min(timeline_data, key=lambda x: x["year"])["year"]
    latest = max(timeline_data, key=lambda x: x["year"])["year"]

    # Get top traditions
    tradition_freq = analysis_service.get_tradition_symbol_frequency()
    traditions_sorted = sorted(tradition_freq, key=lambda x: x["count"], reverse=True)

    return jsonify({
        "total_symbols": len(symbols),
        "total_traditions": len(traditions),
        "time_span": {
            "earliest": earliest,
            "latest": latest,
            "range_years": latest - earliest
        },
        "top_traditions": traditions_sorted[:5]
    })