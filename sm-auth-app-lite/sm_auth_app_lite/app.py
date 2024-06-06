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
    
    ## added this route for startup help
    @app.route('/') 
    def index():
        sth = """ <p> - /google for google auth, fetching token for user & permissions etc. </br>
                    - /api/v1/mailbox for gmail api related actions  </br>
                        - /match -> sends the query to gmail api- returns threads as it is </br>
                        - /fetch -> processess the matched threads to extract emails (each thread can have multiple emails). </br>
                                    Emails are in the form base64 encoded html data. </br>
                        - /process -> takes the encoded emails, turns into html & parses the relevant info using regex.  </br>
                    Ability to pass custom regex/use GPT to do this job.  </br></p>
    """
        return sth
    return app

app = create_app()