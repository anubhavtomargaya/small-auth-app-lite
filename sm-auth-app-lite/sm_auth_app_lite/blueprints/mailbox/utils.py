from flask import current_app as app, jsonify
from sm_auth_app_lite.common.utils import build_credentials
from googleapiclient.discovery import build
from typing import List, Union,Dict

MAILBOX_THREAD_COUNT = None
MAILBOX_MESSAGE_COUNT = None

def get_matched_threads(query,
                     maxResults:int=400,
                     oauth2_client=None):   
    try:
        app.logger.info('building credentials... matched threads ')

        if not oauth2_client :
            raise Exception("No auth client passed ")
        
        app.logger.info('auth client recvd success moving forward:, %s ',oauth2_client)
        threads = oauth2_client.users().threads().list(userId='me',q= query, maxResults=maxResults)
        thread_list = threads.execute().get('threads',[])
        # print(threads)
        MAILBOX_THREAD_COUNT = len(thread_list)
        # print(thread_list)
        # print("threads  ")
        return  [x['id'] for x in thread_list]


    except Exception as e:
        app.logger.exception('getting threads failed')
        raise e
    
def get_matched_threads_list(query,
                     maxResults:int=400,
                     oauth2_client=None):   
    try:
        app.logger.info('building credentials... matched threads ')

        if not oauth2_client :
            raise Exception("No auth client passed ")
        
        app.logger.info('auth client recvd success moving forward:, %s ',oauth2_client)
        threads = oauth2_client.users().threads().list(userId='me',q= query, maxResults=maxResults)
        thread_list = threads.execute().get('threads',[])
        # print(threads)
        MAILBOX_THREAD_COUNT = len(thread_list)
        # print(thread_list)
        # print("threads  ")
        return  thread_list

    except Exception as e:
        app.logger.exception('getting threads failed')
        raise e

class Message:
    def __init__(self, id: str, threadId: str,
                 snippet:str,
                #   historyId:str,
                #    internalDate:str,
                     payload: Dict, **kwargs):
        self.id: str = id
        self.threadId: str = threadId
        self.payload: Dict = payload
        self.snippet = snippet

class ApiCallError(Exception):
    """Custom exception for API call errors."""

def get_messages_by_thread_ids(ids: List[str]) -> Union[List[Message], ApiCallError]:
    """Retrieves messages for specified thread IDs from the API.

    Args:
        ids: A list of thread IDs to fetch messages from.

    Returns:
        List[Message]: A list of Message objects representing the retrieved messages.
        ApiCallError: An exception if an API error occurs.
    """

    messages: List[Message] = []
    oauth2_client = build(
                            'gmail','v1',
                            credentials=build_credentials())
    if not oauth2_client :
        raise Exception("Unable to build oauth client for gmail")
        
    for id in ids:
        try:
            response = oauth2_client.users().threads().get(userId='me', id=id).execute()
            messages_list = response['messages']

            # Efficiently create Message objects directly from parsed JSON
            messages.extend(Message(id=message_data['id'],snippet=message_data['snippet'],historyId=message_data['historyId'],internalDate=message_data['internalDate'], threadId=id, payload=message_data).__dict__ for message_data in messages_list)

        except Exception as e:
            app.logger.exception('Error retrieving messages for thread ID %s: %s', id, e)
            return ApiCallError(f"Failed to fetch messages for thread ID {id}")

    app.logger.info('Thread IDs yielded %s messages', len(messages))
    MAILBOX_MESSAGE_COUNT = len(messages)
    return messages
# 
def get_messages_data_from_threads(ids,
                                   oauth2_client=None):
    """
    service: gmail service built using token
    ids: list of thread Ids to process
    Appends all messages extracted from Threads into a list as RAW messages
    """

    messages_output=[]
    app.logger.info('thread IDs to process: %s',len(ids))
    if isinstance(ids,list):
        try:
            if not oauth2_client :
                raise Exception("No oauth client for gmail")
        
            for id in ids:
                thread =  oauth2_client.users().threads().get(userId='me', id=id).execute()
                messages_list = thread['messages']
                for msg in messages_list:
                    messages_output.append(msg) 
            app.logger.info('thread IDs yield %s messages',len(messages_output))
            MAILBOX_MESSAGE_COUNT = len(messages_output)
            return messages_output
        except Exception as e:
            app.logger.exception('unable to get messages for given thread id(s)')
            return e
    else:
        app.logger.exception('List of Ids expected')
        raise TypeError('List of Ids expected')
    
