from flask import Flask
from config import config_by_name
from routes import main_routes, api_routes
from models.database import db
from flask_migrate import Migrate
import datetime

def create_app(config_name='default'):
    """Application factory pattern for creating Flask app"""
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize SQLAlchemy
    db.init_app(app)

    # Initialize Flask-Migrate
    migrate = Migrate(app, db)

    # Register blueprints
    app.register_blueprint(main_routes.bp)
    app.register_blueprint(api_routes.bp, url_prefix='/api')

    # Add template context processor to inject variables into all templates
    @app.context_processor
    def inject_current_year():
        return {'current_year': datetime.datetime.now().year}

    # Register error handlers
    @app.errorhandler(404)
    def page_not_found(error):
        return 'Page not found', 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return 'Internal server error', 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=app.config['DEBUG'])