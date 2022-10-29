from flask import Flask
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "xsaiodoiewhoesicc"
    app.config['UPLOAD_PATH'] = ".\\website\\uploads\\test1"
    app.config["ALLOWEWD_EXTENSIONS"] = ["SHP", "CPG", "DBF", "SHX", "SBN", "SBX", "XML", "PRJ"]
    
    from .views import views
    
    app.register_blueprint(views, url_prefix='/')
    return app    
