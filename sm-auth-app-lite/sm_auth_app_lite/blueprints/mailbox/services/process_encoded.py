


import base64
import re
from bs4 import BeautifulSoup
from flask import current_app as app

import logging
logger = logging.getLogger(__name__)


def getContentsFromBody(ebd):
        amount_debtied = re.search(r'Rs.\d*', ebd)
        to_vpa = re.search(r'VPA.+?on', ebd)

        date = re.search(r'(\d{2}-\d{2}-\d{2}.*?)(?=\.)', ebd)

        
        if date:
            date = date.group(1)
        else: 
            date = None
        
        if to_vpa:
            to_vpa = to_vpa.group().strip('VPA  on')
        else: 
            to_vpa = None
        if amount_debtied:
            amount_debtied = amount_debtied.group().strip('Rs.')
        else: 
            amount_debtied = None
        
        return date,to_vpa,amount_debtied

def getEmailBody(coded_body):
    """ trys to find the relevand html tag in the email that contains the data """
    data = coded_body.replace("-","+").replace("_","/")
    decoded_data = base64.b64decode(data)
    soup = BeautifulSoup(decoded_data , "html.parser")
    # app.logger.info(soup)
    email_body = soup.find_all('td',{"class": "td"})[0].text
    if len(email_body) <20: #was taking an empty td as 0th element of list
        email_body = soup.find_all('td',{"class": "td"})[1].text
   
    return email_body


def extractBodyFromEncodedData(coded_relevant_json):
    """ not giving a shit about the previous function or the global stage param, just
        needs the key msgEncodedData to be there fks off to do the job 
    """

    try:
        app.logger.info('type of input %s',type(coded_relevant_json))
     
        decoded_extracted_info = []
        failed_first_box = []
       
        for txn in coded_relevant_json:
            # logger.info('message %s',message)
            try:
                if not isinstance(txn,dict):
                    message = txn.__dict__['__data__']
                else:
                    message = txn

                data = message['msgEncodedData']  
                email_body = getEmailBody(data)
                date,to_vpa,amount_debtied = getContentsFromBody(email_body)

                message['date']= date
                message['to_vpa']= to_vpa
                message['amount_debited']= amount_debtied
                del message['msgEncodedData']
                # if amount_debtied ==None or date==None or to_vpa==None:
                #     pass
                # else:
                decoded_extracted_info.append(message)
            except Exception as e:
                app.logger.exception('error extracting message id %s,',e)
                failed_first_box.append(message['msgId'])
                return ("ExtractionError:",e)

        app.logger.info('size of output messages %s',len(decoded_extracted_info))

        return decoded_extracted_info
            
    except Exception as e:
        # decoded_extracted_info
        logger.exception('error in extracting transaction info')
        return e