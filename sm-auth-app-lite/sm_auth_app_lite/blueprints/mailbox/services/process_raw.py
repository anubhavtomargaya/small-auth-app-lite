from flask import current_app as app
from playhouse.shortcuts import model_to_dict, dict_to_model
from sm_auth_app_lite.common.db_init import RawTransactions


def parse_gmail_message(msg):
    """Parses a Gmail API message and extracts relevant data.

    Args:
        msg (dict): The message dictionary from the Gmail API response.

    Returns:
        dict (or None): A dictionary containing extracted data or None if no
                         text content is found.
    """
    print("inside ss")
    payload = msg.get('payload')
    if not payload:
        return None  # Handle missing payload gracefully

    # Check for single-part (text/html or text/plain) message first
    if payload.get('mimeType') in ('text/html', 'text/plain'):
        data = payload.get('body').get('data')
        if data:
            return {
                'msgId': msg.get('id'),
                'threadId': msg.get('threadId'),
                'snippet': msg.get('snippet'),
                'msgEpochTime': msg.get('internalDate'),
                'msgEncodedData': data,
            }

    # If not single-part, handle multipart/mixed recursively
    elif payload.get('mimeType') == 'multipart/mixed':
        parts = payload.get('parts')
        for part in parts:
            extracted_data = parse_gmail_message(part)
            if extracted_data:
                return extracted_data

    # No text content found
    return None

class EmailMessage:
    """ msg recvd from thread"""
    def __init__(self, msg_id, thread_id, snippet, msg_epoch_time):
        self.msg_id = msg_id
        self.thread_id = thread_id
        self.snippet = snippet
        self.msg_epoch_time = msg_epoch_time

class EmailContent(EmailMessage):
    """ encoded data found after recursing through parts"""
    def __init__(self, msg_id, thread_id, snippet, msg_epoch_time, msg_encoded_data):
        super().__init__(msg_id, thread_id, snippet, msg_epoch_time)
        self.msg_encoded_data = msg_encoded_data

def extractCodedContentFromRawMessages(email_messages:list):
    """Works like mapper for RAW MESSAGES
    Args:
        email_messages (list): RAW returned by gmail service
    """
   
    
    app.logger.info('Input messages to process: %s',len(email_messages))
    return_list = []
    for msg in email_messages: ### while loop to listen to stream
        app.logger.info('processing message: %s',msg['id'])
        try: #map and save

            if not isinstance(msg,dict):
                raise TypeError("input expected to be json")
            if not msg.get('payload'):
                raise ValueError("Expecting 'payload' as the key")
            payload = msg['payload']

            row = RawTransactions()
            row.msgId=msg['id']
            row.threadId=msg['threadId']
            row.snippet=msg['snippet']
            row.msgEpochTime=msg['internalDate']
            row.msghistoryId=msg['historyId']
   
            if payload['mimeType'] =='text/html':
                app.logger.info('mimeType found text/html')
                row.msgEncodedData = payload['body']['data']
                # row = payloadDataMapper(payldata)
                # messages_extracted_from_threads =extractHTMLMimeType(msg)
                # row.save()
                return_list.append(model_to_dict(row))
            else:
                app.logger.info('mimeType found as other, looping again')
                parts = payload['parts']
                for payld in parts:
                    if payld['mimeType'] =='text/html':
                        app.logger.info('mimeType found as text/html')
                        row.msgEncodedData = payld['body']['data']
                        # row.save()
                        # messages_extracted_from_threads =extractHTMLMimeType(data)
                        return_list.append(model_to_dict(row))
                    else:
                        app.logger.exception('No mime Type matched')   
        except Exception as e:
            app.logger.exception('MappingError: for the message id %s',msg['id'])
            return e
        
    app.logger.info('messages extracted %s \n messages given: %s',len(return_list),len(email_messages))
    return return_list

