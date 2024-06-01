from flask import  current_app
import googleapiclient.discovery

from  sm_auth_app_lite.common.utils import build_credentials

def get_user_info():
    try:
        current_app.logger.info('Building credentials..user info')
        oauth2_client = googleapiclient.discovery.build('oauth2',
                                                        'v2',
                                                        credentials= build_credentials())
        return oauth2_client.userinfo().get().execute()
    except Exception as e:
        current_app.logger.exception('Building credentials failed')
        return e