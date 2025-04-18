class Config:
    """Application configuration"""
    DEBUG = True
    SECRET_KEY = 'dev-key-would-be-changed-in-production'
    JSON_SORT_KEYS = False

    # Add additional configuration settings here
    # For example:
    # DATABASE_URI = 'sqlite:///occult_symbols.db'  # if you add a database later
    # UPLOAD_FOLDER = 'uploads'  # if you add file upload capabilities


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    # In production, you would use a more secure secret key
    SECRET_KEY = 'this-would-be-a-secure-key-in-production'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True


# Configuration dictionary to easily select environment
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}