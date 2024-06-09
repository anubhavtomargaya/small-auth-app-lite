

from authlib.client import OAuth2Session
from flask import current_app, url_for, redirect
import flask 
import ast
import json 

from sm_auth_app_lite.common.session_manager import set_auth_state,set_auth_token, clear_auth_session, get_next_url,is_logged_in
from sm_auth_app_lite.common.constants import *
from .auth import get_user_info


from . import google_auth, no_cache



@google_auth.route('/login')
@no_cache
def login():

        
    if is_logged_in():
        return "Already logged in, proceed to api/v1/mailbox"
    # redirect(url_for('index'))
    current_app.logger.info("RUNNING LOGIN")
    current_app.logger.info('building session')
    session = OAuth2Session(CLIENT_ID, CLIENT_SECRET,
                            scope=AUTHORIZATION_SCOPE,
                            redirect_uri= url_for('google_auth.google_auth_redirect',
                                                 _external=True)) #no need to use 
                                                        #AUTH_REDIRECT_URI

    uri, state = session.create_authorization_url(AUTHORIZATION_URL)
    current_app.logger.debug("state %s",state )
    current_app.logger.debug("uri %s",uri)
    set_auth_state(state)

    return flask.redirect(uri, code=302)

@google_auth.route('/auth')
@no_cache
def google_auth_redirect():
    # current_app.logger.info("keys!! %s",flask.session.keys())
    req_state = flask.request.args.get('state', default=None, type=None)
    current_app.logger.debug('req state!!: %s',req_state)
    # if req_state != flask.session[AUTH_STATE_KEY]:
    #     response = flask.make_response('Invalid state parameter', 401)
    #     return response
    try:
        current_app.logger.info('creating session')
        session = OAuth2Session(CLIENT_ID, CLIENT_SECRET,
                                scope=AUTHORIZATION_SCOPE,
                                state=req_state,
                                redirect_uri=
                                        url_for('google_auth.google_auth_redirect',
                                        _external=True))
    except Exception as e:
        return flask.jsonify(e)
    current_app.logger.debug(' session built')
        
    oauth2_tokens = session.fetch_access_token(
                        ACCESS_TOKEN_URI,            
                        authorization_response=flask.request.url)

    current_app.logger.debug('oath tokens!! : %s',oauth2_tokens)
    set_auth_token(oauth2_tokens)
    default_login_url = url_for('google_auth.etc',data=oauth2_tokens)

    next_url = get_next_url()
    current_app.logger.info(' next url %s',next_url) 
    if next_url:

        current_app.logger.info(' next url %s',next_url) 
        # clear_next_url()
        return flask.redirect(next_url, code=307)
    else: 
        return flask.redirect(default_login_url, code=307)
    

@google_auth.route('/logout')
@no_cache
def logout():
    # flask.session.pop(AUTH_TOKEN_KEY, None)
    # flask.session.pop(AUTH_STATE_KEY, None)
    clear_auth_session()
    
    return flask.redirect(BASE_URI, code=302)


@google_auth.route('/etc')
def etc():
    
    d=flask.request.args['data']
   
    d = ast.literal_eval(d)
    current_app.logger.info('body: %s',d)
    current_app.logger.info('type: %s',type(d))
    if is_logged_in():
        user_info = get_user_info()
        current_app.logger.info(user_info)
        name=user_info['given_name']
        expiresat=d['expires_at']
        val=d['access_token'][0:6]
        # curr_pth = pathlib.Path(__file__).resolve().parent
        # tkdir = pathlib.Path('temp','etc')
        # filename=f'token_{name}_{val}_{expiresat}_.json'
      
        # filepath = pathlib.Path(curr_pth,tkdir,filename)
        # with open(filepath,'w') as f:
            # print(json.dump(dew,f))
        
        ###check if not able to save file in ec2

        return '<div>You are currently logged in as ' + user_info['given_name'] + '<div><pre>' + json.dumps(user_info, indent=4) + "</pre>"
    # flask.redirect(BASE_URI, code=302)
    else:
        # return render_template("index.html")

        return flask.jsonify("ERORROR )")

