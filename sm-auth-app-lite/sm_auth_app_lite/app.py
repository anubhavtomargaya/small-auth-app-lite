""" 
Using application factory, i.e. create_app() contains all the steps involved in
creating the flask application. due to which some routes are also inside this 
function. They can be added as a blueprint but I am using these as tools while 
developement. Run this with run.py" 
"""
from flask import Flask
from flask_cors import CORS
import logging
from sm_auth_app_lite.common import fh
from sm_auth_app_lite.blueprints.google_auth import google_auth
from sm_auth_app_lite.blueprints.mailbox import gmail_app
from sm_auth_app_lite.blueprints.gmail import gmail_bp
from sm_auth_app_lite.common.session_manager import *

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
    
    app.register_blueprint(gmail_bp, url_prefix='/api/v1/gmail')
    app.logger.info('Flask bp registerd, %s',"/gmail")
    
    ## added this route for startup help
    @app.route('/') 
    def index():
        sth = """ <p> - /google for google auth, fetching token for user & permissions etc. </br>
                    - /api/v1/mailbox for gmail api related actions  </br>
                    - /api/v1/gmail for new Gmail service endpoints  </br>
                        - /search -> search emails with query parameters </br>
                        - /hdfc -> get and process HDFC transactions </br></p>
    """
        return sth
    return app

app = create_app()