from flask import Flask
from secret_key_generator import secret_key_generator
from os import path
from flask_login import LoginManager

def create_app():
    SECRET_KEY = secret_key_generator.generate()
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY

    from .views import views
    app.register_blueprint(views, url_prefix="/")

    return app
