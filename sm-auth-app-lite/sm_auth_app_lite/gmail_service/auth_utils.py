from typing import Dict
from .models.credentials import GmailCredentials
# from ..common.session_manager import get_auth_token
from ..common.constants import CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN_URI
import requests
from typing import Optional
from .exceptions import AuthError

def get_gmail_credentials() -> GmailCredentials:
    """Get Gmail credentials from existing auth system"""
    try:
        # Get tokens from your existing auth system
        oauth2_tokens = get_auth_token()
        if not oauth2_tokens:
            raise ValueError("No auth tokens found")
            
        # Convert to Gmail service format
        return GmailCredentials(
            token=oauth2_tokens['access_token'],
            refresh_token=oauth2_tokens['refresh_token'],
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            token_uri=ACCESS_TOKEN_URI
        )
    except Exception as e:
        raise Exception(f"Failed to get Gmail credentials: {str(e)}")

def validate_credentials(credentials: GmailCredentials) -> bool:
    """Simple validation of credentials"""
    return bool(
        credentials 
        and credentials.token 
        and credentials.refresh_token
    ) 

def get_credentials_from_server(server_url: str = "http://localhost:5000") -> GmailCredentials:
    """Get Gmail credentials from auth server"""
    try:
        response = requests.get(
            f"{server_url}/google/credentials",
            cookies=requests.cookies.RequestsCookieJar()  # Will carry session cookie if exists
        )
        
        if response.status_code == 401:
            raise AuthError("Not authenticated. Please login first.")
            
        if response.status_code != 200:
            raise AuthError(f"Failed to get credentials: {response.json().get('message')}")
            
        cred_data = response.json()['credentials']
        return GmailCredentials(**cred_data)
        
    except Exception as e:
        raise AuthError(f"Failed to get credentials from server: {str(e)}") 

def get_credentials_from_tokens(tokens: Dict[str, str]) -> GmailCredentials:
    """Create Gmail credentials from OAuth tokens"""
    return GmailCredentials(
        token=tokens['access_token'],
        refresh_token=tokens['refresh_token'],
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        token_uri=ACCESS_TOKEN_URI
    ) 