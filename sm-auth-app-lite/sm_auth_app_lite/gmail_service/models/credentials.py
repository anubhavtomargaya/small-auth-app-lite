from dataclasses import dataclass
from typing import List, Optional

@dataclass
class GmailCredentials:
    """Gmail OAuth2 credentials model"""
    token: str
    refresh_token: str
    token_uri: str = "https://oauth2.googleapis.com/token"
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    scopes: List[str] = None

    def __post_init__(self):
        """Set default scopes if none provided"""
        if self.scopes is None:
            self.scopes = [
                'https://www.googleapis.com/auth/gmail.readonly',
                'https://www.googleapis.com/auth/gmail.modify'
            ]

    def to_dict(self) -> dict:
        """Convert to dictionary format for google-auth"""
        return {
            'token': self.token,
            'refresh_token': self.refresh_token,
            'token_uri': self.token_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scopes': self.scopes
        }

    @classmethod
    def from_oauth_tokens(cls, oauth2_tokens: dict, client_id: str, client_secret: str) -> 'GmailCredentials':
        """Create GmailCredentials from OAuth2 tokens"""
        return cls(
            token=oauth2_tokens['access_token'],
            refresh_token=oauth2_tokens['refresh_token'],
            client_id=client_id,
            client_secret=client_secret
        )

    def is_valid(self) -> bool:
        """Basic validation of required fields"""
        return bool(
            self.token 
            and self.refresh_token 
            and self.client_id 
            and self.client_secret
        ) 