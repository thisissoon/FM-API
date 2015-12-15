# Standard Libs
import logging


# Default Logging Configuration
DEFAULT_LOG_LEVEL = 'INFO'
DEFAULT_LOG_FORMAT = "%(levelname)s [%(asctime)s]: %(message)s"


def configure(app):
    """Configures logging for the Flask Application.
    Arguments
    ---------
    app : flask.app.Flask
        Flask application instance
    """

    # Reset the handlers
    app.logger.handlers = []

    # Setup Stream Handler
    handler = logging.StreamHandler()
    # Set Format
    try:
        handler.setFormatter(logging.Formatter(app.config['LOG_FORMAT']))
    except KeyError:
        handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))

    # Set Level
    try:
        level_name = app.config['LOG_LEVEL']
    except KeyError:
        level_name = DEFAULT_LOG_LEVEL

    level = getattr(logging, level_name.upper(), logging.INFO)

    # Update the app logger
    app.logger.setLevel(level)
    app.logger.addHandler(handler)
