import os

from flask import Flask


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "washmaster.sqlite"),
    )

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # register the database commands
    from . import db
    db.init_app(app)

    # apply the blueprints to the app
    from . import auth
    from . import overview

    app.register_blueprint(auth.bp)
    app.register_blueprint(overview.bp)

    return app
