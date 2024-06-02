from flask import current_app as app
import google.oauth2.credentials
from .constants import CLIENT_ID,CLIENT_SECRET,ACCESS_TOKEN_URI
from .session_manager import is_logged_in,get_auth_token

## modify this to take auth tokens as input
def build_credentials(oauth2_tokens=None):
    try:
        if not oauth2_tokens:    
            if not is_logged_in():
                app.logger.warning('user to be logged in')
                raise Exception('AuthError: User must be logged in')
            #read from session afterwards
            oauth2_tokens = get_auth_token()
            if not oauth2_tokens:
                raise Exception("Cant get auth tokens") 
        
        return google.oauth2.credentials.Credentials(
                    oauth2_tokens['access_token'],
                    refresh_token=oauth2_tokens['refresh_token'],
                    client_id=CLIENT_ID,
                    client_secret=CLIENT_SECRET,
                    token_uri=ACCESS_TOKEN_URI)
    except Exception as e:
        raise Exception(F"Error Building Credentials : {e}")
    
from googleapiclient.discovery import build

def get_oauth_client(token):
    oauth2_client = build('gmail','v1',
                            credentials=build_credentials(oauth2_tokens=token))
    if not oauth2_client :
        app.logger.info('building credentials error, %s ',oauth2_client)
        raise Exception("Unable to build oauth client for gmail")
    
    app.logger.info('building credentials success moving forward:, %s ',oauth2_client)
    return oauth2_client



import datetime
import uuid

def get_now_time_string():

    end_time = datetime.datetime.utcnow().replace(tzinfo=None)
    return end_time.__str__()


def get_random_execution_id():
    """Generates a random, lightweight execution ID using UUID."""
    return str(uuid.uuid4())[:8]  # Use the first 8 characters for brevity