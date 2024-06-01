from flask import session

FLAST_NEXT_URL_KEY = 'next_url' 
AUTH_TOKEN_KEY = 'auth_token'
AUTH_STATE_KEY = 'oauth_state'
EXEC_ID_KEY = 'execution_id'
EMAIL_MESSAGES = 'email_messages'

def set_auth_token(token):
    session[AUTH_TOKEN_KEY] = token

def set_exec_key(exec_id):
    session[EXEC_ID_KEY] = exec_id

def get_exec_key():
    return session.get(EXEC_ID_KEY, None)

def set_email_list(email_list):
    session[EMAIL_MESSAGES] = email_list

def get_email_list():
    return session.get(EMAIL_MESSAGES, None)

def clear_email_list():
    return session.pop(EMAIL_MESSAGES, None)

def get_auth_token():
    return session.get(AUTH_TOKEN_KEY, None)

def set_auth_state(state):
    session['permanent'] = True
    session[AUTH_STATE_KEY] = state

def get_auth_state():
    return session.get(AUTH_STATE_KEY, None)

def clear_auth_session():
    session.pop(AUTH_TOKEN_KEY, None)
    session.pop(AUTH_STATE_KEY, None)

def is_logged_in():
    return AUTH_TOKEN_KEY in session

##next url for redirection

def set_next_url(url):
    session[FLAST_NEXT_URL_KEY] = url

def get_next_url(default_url=None):
        return session.get(FLAST_NEXT_URL_KEY, default_url)

def clear_next_url():
        session.pop(FLAST_NEXT_URL_KEY, None)

def get_session_keys():
    return list(session.keys())

def get_session_items():
    return list(session.items())