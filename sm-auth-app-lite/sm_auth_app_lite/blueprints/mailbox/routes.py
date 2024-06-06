from http.client import HTTPException

from . import gmail_app
from google.auth.exceptions import RefreshError
import requests,json,datetime
from flask import current_app as app,jsonify,request, url_for, redirect,render_template
from sm_auth_app_lite.common.session_manager import clear_email_list, get_auth_token, get_email_list, get_exec_key, is_logged_in, set_exec_key,set_next_url
from sm_auth_app_lite.blueprints.mailbox.fetch_by_token import TokenFetchRequest,fetch_matching_messages, process_raw_messages, search_messages

# stats_dict = {
#         "MAILBOX_THREAD_COUNT" :None,
#         "MAILBOX_MESSAGE_COUNT" : None,
#         "RAW_MESSAGE_COUNT":None,
#         "TRANSACTION_MESSAGE_COUNT":None
#         }


@gmail_app.route('/',methods=['GET','POST'])
def index():
    if not is_logged_in():
        set_next_url(url_for('gmail_app.index'))
        app.logger.info("not logged int")
        return redirect(url_for('google_auth.login'))
    else:
        app.logger.info("logged int")
        return render_template('home.html') ##gmail_app > index.html
    

@gmail_app.route('/match/',methods=['GET']) 
def match_emails_for_query():
    """ saves no state anywhere, returns the matching threads for the query as returned by gmail """

    mthd = request.method 
    args = request.args
    app.logger.info('method: %s',mthd)
    app.logger.info('args: %s',args)
    if not mthd =='GET':
        raise HTTPException("Invalid HTTP Method for the endpoing %s",mthd)

    ###prcess arguements
    num_days = args.get('num_days') or 3
    email = args.get('email') or  'alerts@hdfcbank.net'
    today_ist = datetime.datetime.now()
    app.logger.info("todat %s",today_ist)
    # app.logger.info("rype",type(today_ist))
    et = today_ist.strftime('%Y-%m-%d')
    start_ist = today_ist - datetime.timedelta(days=int(num_days))
    st = start_ist.strftime('%Y-%m-%d')
    app.logger.info('st,et:  %s %s',st,et)
    
    # access mailbox
    try:
        if not is_logged_in():
            raise HTTPException("User not logged in!")

        token = get_auth_token()
        rq = TokenFetchRequest(token=token,
                                start=st,
                                email=email,
                                end=et)
        print("searching for messages")
        print(rq.__dict__)
        return jsonify(search_messages(rq))
    
    except RefreshError as re:
        app.logger.info('refresh error %s',re)
        return redirect(url_for('google_auth.logout'))

@gmail_app.route('/fetch/',methods=['GET']) 
def fetch_emails_for_query():
    mthd = request.method 
    args = request.args
    app.logger.info('method: %s',mthd)
    app.logger.info('args: %s',args)
    if not mthd =='GET':
        raise HTTPException("Invalid HTTP Method for the endpoing %s",mthd)

    ###prcess arguements
    num_days = args.get('num_days') or 3
    email = args.get('email') or  'alerts@hdfcbank.net'
    today_ist = datetime.datetime.now()
    app.logger.info("todat %s",today_ist)
    # app.logger.info("rype",type(today_ist))
    et = today_ist.strftime('%Y-%m-%d')
    start_ist = today_ist - datetime.timedelta(days=int(num_days))
    st = start_ist.strftime('%Y-%m-%d')
    app.logger.info('st,et:  %s %s',st,et)
    
    # access mailbox
    if not is_logged_in():
        raise HTTPException("User not logged in!")

    try:
        token = get_auth_token()
        rq = TokenFetchRequest(token=token,
                                start=st,
                                end=et,
                                email=email)
        
        return jsonify(fetch_matching_messages(rq))
    
    except RefreshError as re:
        app.logger.info('refresh error %s',re)
        return redirect(url_for('google_auth.logout'))

@gmail_app.route('/process/',methods=['GET']) 
def process_email_list():
    # execution_id = get_random_execution_id()

    email_list = get_email_list()
    if not email_list:
        # return jsonify("No messages in session")
        raise HTTPException("No emails found in session. First use api/v1/fetch or POST ids")
    
    # run process service 

    print("email lst", email_list)
    processed_emails_response = process_raw_messages(email_list)
    # processed_emails_response['session_email_list']= email_list
    clear_email_list() #clear session vals to denote that no pending emails to process
   
    return jsonify(processed_emails_response)
