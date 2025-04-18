from flask import Blueprint, render_template
from datetime import datetime

# Create Blueprint
bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Render the main dashboard page"""
    return render_template('index.html')

@bp.route('/about')
def about():
    """Render the about page"""
    return render_template('about.html')