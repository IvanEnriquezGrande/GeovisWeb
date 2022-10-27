from flask import Flask
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "xsaiodoiewhoesicc"
    app.config['UPLOAD_PATH'] = "D:\\Programas\\Python\\geovis\\src\\website\\uploads\\test1"
    
    from .views import views
    
    app.register_blueprint(views, url_prefix='/')
    return app    
