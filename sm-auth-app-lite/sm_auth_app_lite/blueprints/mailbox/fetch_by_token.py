

import datetime
import json
from flask import jsonify, current_app as app
from sm_auth_app_lite.common.utils import get_now_time_string, get_random_execution_id
from sm_auth_app_lite.common.db_handler import  insert_final_transactions,insert_raw_transactions, query_raw_messages
from sm_auth_app_lite.common.models import  TokenFetchRequest, SearchResponse, MatchResponse


from google.auth.exceptions import RefreshError
from sm_auth_app_lite.common.utils import get_oauth_client

from sm_auth_app_lite.common.session_manager import set_exec_key,get_exec_key,set_email_list,get_email_list
from sm_auth_app_lite.blueprints.mailbox.services.process_encoded import extractBodyFromEncodedData
from .query import get_query_for_email

from .utils import get_matched_threads, get_matched_threads_list, get_messages_data_from_threads
from .services.process_raw import extractCodedContentFromRawMessages


def get_mesaages_to_parse(existing_msgs:list,
                          inserted_msgs:list,
                          include_existing:bool=False):
    
    app.logger.info("inserted now looks %s",inserted_msgs)
    proc = []
    if len(existing_msgs) > 0 and include_existing: 
        # should its needed to process the 
        # existing again, do here
        proc.extend(existing_msgs)
        print("inserted now looks",inserted_msgs)

    if len(inserted_msgs) > 0: 
        proc.extend(inserted_msgs)
    if not len(proc) > 0:
        app.logger.warning("Nothing to insert")
   
    return query_raw_messages(proc,column=None)


def search_messages(request:TokenFetchRequest):
    """ saves no state anywhere, returns the matching threads for the query as returned by gmail """
    try:
        
        execution_id = get_random_execution_id()
        set_exec_key(execution_id)
        exec_start_time = get_now_time_string()
        oauth2_client = get_oauth_client(token=request.token)
        mailbox_query = get_query_for_email(start=request.start,end=request.end,email=request.email)
        print(mailbox_query)
        thread_list = get_matched_threads_list(mailbox_query,oauth2_client=oauth2_client) #log output 
        response = SearchResponse(threads=len(thread_list),
                                    query_string=mailbox_query,
                                    data= {"threads":thread_list})
        
       
        return response.__dict__

    except RefreshError as re:
        raise re

def fetch_matching_messages(request:TokenFetchRequest):
    """ starts execution -> sets execution id. 
      todo: updates job time meta according to meta dict in session key `execid` 
       builds oauth client and query for the input in request 
        queries mailbox to get matching threads -> use them to get messages (end user doesnt know about threads)

          """
    try:
        
        execution_id = get_random_execution_id()
        set_exec_key(execution_id)
        exec_start_time = get_now_time_string()
        oauth2_client = get_oauth_client(token=request.token)
        mailbox_query = get_query_for_email(start=request.start,end=request.end,email=request.email)
        thread_ids = get_matched_threads(mailbox_query,oauth2_client=oauth2_client) #log output 
        email_msgs_list = get_messages_data_from_threads(thread_ids,oauth2_client=oauth2_client)
        # set_email_list(email_msgs_list)
        match_end_time = get_now_time_string()
        response = MatchResponse(threads=len(thread_ids),
                                    messages=len(email_msgs_list),
                                    query_string=mailbox_query,
                                    data= {"msgs_list":None})
        
        raw_coded_msgs = extractCodedContentFromRawMessages(email_msgs_list)
        db_response = insert_raw_transactions(execution_id, raw_coded_msgs)
        app.logger.info("db res %s", db_response.__dict__)
        msgs = db_response.existing_msgs
        msgs.extend(db_response.inserted_msgs)
        app.logger.info("msgs %s", msgs)

        set_email_list(msgs)
        response.data['msgs_list'] = msgs
        return response.__dict__

    except RefreshError as re:
        raise re

def process_raw_messages(email_message_ids:list,
                         execution_id:str=None):

    app.logger.info("size %s , msgs to_proc %s",len(email_message_ids),email_message_ids)
    app.logger.info("start to_proc %s",get_now_time_string())
    # pass the email inside as a mapping for regex
    to_insert  = extractBodyFromEncodedData(get_mesaages_to_parse(existing_msgs=[],
                                                               inserted_msgs=email_message_ids,
                                                                include_existing=False)) # pass here: regex mapping 
    app.logger.info("end to_proc %s",get_now_time_string())
    app.logger.info("to_proc %s",to_insert)
    return to_insert 
    if to_insert: # escaping the code to insert and return in a standard way
        processed_emails_response = insert_final_transactions(execution_id, to_insert)
        app.logger.info("out_yeild %s",processed_emails_response)
        return processed_emails_response
    # meta_entry.decoded_message_count = len(out_yeild['inserted']

if __name__ == '__main__':
    

    """ expected token format in TokenFetchRequest:"""
    sample_token = {'access_token': 'ya29.a0AfB_byCyywmiQtN4ufGZVC--XINWOaG8RHorBSR-ZWWRfLWKFD6fWzNAbdEPj2fW7mV_WCxNrADH1gdHIIAZqEdjeN8eS6XtCngcosMgXpc7_SIjydFkKCAPbqvMpiA7ZcccA6oNMT__zIL7pVsALt57bBxOGZqRP8W9aCgYKATkSARISFQHGX2MiX5ss9_IOR_shtGMB5mqB0A0171', 'expires_at': 1708978287, 'expires_in': 3599, 'id_token': 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjU1YzE4OGE4MzU0NmZjMTg4ZTUxNTc2YmE3MjgzNmUwNjAwZThiNzMiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiI0ODMxMjQ1MzM3MDItMG1ndnMyNGVic3VqOWY5Z2FldGJ2OHZndjdtcm4zMzMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJhdWQiOiI0ODMxMjQ1MzM3MDItMG1ndnMyNGVic3VqOWY5Z2FldGJ2OHZndjdtcm4zMzMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMDM2NjYyMDAxNTQxMTY3NzQ5MzUiLCJlbWFpbCI6ImltYW51YmhhdjE4QGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJhdF9oYXNoIjoiVnFJS3k1QTltc3RBYThILUF0TzltUSIsIm5hbWUiOiJBbnViaGF2IFRvbWFyIiwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FDZzhvY0pXNEhCcGw1dFFBRDFTcWo5Mm1NZUNnRF9POGVBX2c1RFNKUjg5Zmp1MFZIND1zOTYtYyIsImdpdmVuX25hbWUiOiJBbnViaGF2IiwiZmFtaWx5X25hbWUiOiJUb21hciIsImxvY2FsZSI6ImVuLUdCIiwiaWF0IjoxNzA4OTc0Njg4LCJleHAiOjE3MDg5NzgyODh9.k0p4lNyPT_vI2gLlFVP7evVr9Z8PJg3o7rKUnvbwXzGfkMhJjiiaH7sSr8NpAlwqFWDuO4ZrKetzC7s9QugAmcBy1jjcxt2ZTg5Ouv9Us91GqNRIlbwCYr87OT2L9K56H6IT2z_jeGi-XpDFdq7aDSrM3ZDoulP_pSr10WO3DwuBNjepcmMiJexuspdCTPUCYodt8MuvwzWzyPUBzM565UH6jlf6CNfaVCKKQoC31URFatEqn_GDqWz0PbUPqjwQp6qfh1qUHCNoiVwD8avajIRAHWzVWId0O249KDP7JxhBw6uikx0KWinfpAHDvbLKnBO_zmw6GHRkt900viSGqw', 'refresh_token': '1//0g2fx5fS0ZZNNCgYIARAAGBASNwF-L9Iri8d0aIats_a-9kniIHIufltNXj67WlJ-HDuZTqFWchdDIYLPIvAXYf6WFLOB6OEbEVk', 'scope': 'openid https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/gmail.readonly', 'token_type': 'Bearer'}
    sample_request = TokenFetchRequest(token=sample_token,
                                    start='2024-02-23',
                                    end='2024-02-27',
                                    email=None)
