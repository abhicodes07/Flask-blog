import os
from flask import Flask

def create_app(test_config=None):
    # create and configure the app
    # the __name__ refers to the current python module
    app = Flask(__name__, instance_relative_config=True)

    # set some default configuration for the app
    app.config.from_mapping(
        #HACK: should be overridden with a random value when deploying
        SECRET_KEY='dev', # used keeping things safe 
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite') # path where the SQLite database file will be saved
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        #load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    
    @app.route('/hello')
    def hello():
        return 'Hello, world! This is Flask'
    
    from . import db
    from . import auth

    app.register_blueprint(auth.bp)
    db.init_app(app)
    
    return app