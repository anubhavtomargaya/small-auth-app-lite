""" 
Using application factory, i.e. create_app() contains all the steps involved in
creating the flask application. due to which some routes are also inside this 
function. They can be added as a blueprint but I am using these as tools while 
developement. Run this with run.py" 
"""
from flask import Flask,redirect, url_for,render_template,current_app,jsonify
from flask_cors import CORS,cross_origin
import logging
from common import fh
from blueprints.google_auth import google_auth
from blueprints.mailbox import gmail_app
from common.session_manager import *

logging.basicConfig(level=logging.INFO)  
EMAIL_LIST = ['alerts@hdfcbank.net']

def create_app():
    app = Flask(__name__)
    # app.logger.addHandler(file_handler)
    app.logger.addHandler(fh)
    app.logger.info('Flask app started')
    CORS(app)
    app.logger.info('Flask app CORSed')

    app.secret_key = "MYSK3Y"
    # # os.environ.get("FN_FLASK_SECRET_KEY", default=False)

    app.register_blueprint(google_auth, url_prefix='/google')
    app.logger.info('Flask bp registerd, %s',"/google")

    app.register_blueprint(gmail_app, url_prefix='/api/v1/mailbox')
    app.logger.info('Flask bp registerd, %s',"/mailbox")
    return app

app = create_app()
