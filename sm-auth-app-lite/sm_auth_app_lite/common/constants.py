import json
from pathlib import Path
# export PYTHONPATH=/Users/anubhavtomar/2024_projects/small-auth-app-lite/sm-auth-app-litPYTHONPATH

ACCESS_TOKEN_URI = 'https://www.googleapis.com/oauth2/v4/token'
# "https://oauth2.googleapis.com/token"
AUTHORIZATION_URL ='https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&prompt=consent'
# "https://accounts.google.com/o/oauth2/auth"
AUTHORIZATION_SCOPE =["https://www.googleapis.com/auth/gmail.readonly","https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"]
# 'openid email profile'
# ['https://www.googleapis.com/auth/gmail.readonly','openid','email']

AUTH_REDIRECT_URI ="http://localhost:5000/google/auth"
#  os.environ.get("FN_AUTH_REDIRECT_URI", default=False)
BASE_URI =   "http://localhost:5000/"
BASE_REDIRECT_URI =   "http://localhost:5000/fetch"
# os.environ.get("FN_BASE_URI", default=False)
with open(Path(Path(__file__).parent.resolve(), 'env.json')) as f:
    env = json.load(f)

CLIENT_ID = env.get('CLIENT_ID')
# os.environ.get("FN_CLIENT_ID", default=False)
CLIENT_SECRET = env.get('CLIENT_SECRET')
# os.environ.get("FN_CLIENT_SECRET", default=False)

