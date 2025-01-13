from typing import List, Optional, Union
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from .models.credentials import GmailCredentials
from .models.message import EmailMessage
from .models.query import EmailQuery
from .exceptions import GmailError, AuthError
from .processors.base import BaseProcessor

class GmailClient:
    """Gmail API client wrapper"""
    
    def __init__(self, credentials: GmailCredentials):
        self._validate_credentials(credentials)
        self.credentials = credentials
        self.service = self._build_service()
        
    def _validate_credentials(self, credentials: GmailCredentials) -> None:
        """Validate Gmail credentials"""
        if not isinstance(credentials, GmailCredentials):
            raise AuthError("Invalid credentials type")
        if not credentials.is_valid():
            raise AuthError("Invalid credentials: missing required fields")
            
    def _build_service(self):
        """Build Gmail API service"""
        try:
            google_creds = Credentials(**self.credentials.to_dict())
            return build('gmail', 'v1', credentials=google_creds)
        except Exception as e:
            raise GmailError(f"Failed to build Gmail service: {str(e)}")
            
    def get_recent(self, days: int = 7, max_results: int = 10) -> List[EmailMessage]:
        """Get recent emails using direct messages.list API"""
        try:
            # Get messages directly using messages.list
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results,
                labelIds=['INBOX']  # Only get INBOX messages
            ).execute()
            
            messages = []
            message_list = results.get('messages', [])
            
            if not message_list:
                print("No recent messages found")
                return []
                
            for msg in message_list:
                # Get full message details
                full_msg = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                
                # Convert to EmailMessage
                email = EmailMessage.from_gmail_message(full_msg)
                
                # Filter by date if needed
                if days:
                    cutoff_date = datetime.now() - timedelta(days=days)
                    if email.internal_date and email.internal_date < cutoff_date:
                        continue
                        
                messages.append(email)
                
            return messages
            
        except Exception as e:
            print(f"Failed to get recent messages: {str(e)}")
            raise GmailError(f"Failed to get recent messages: {str(e)}")
        
    def search(self, query: EmailQuery, processor: Optional[BaseProcessor] = None) -> List[EmailMessage]:
        """Search emails with query"""
        try:
            # Execute search
            results = self.service.users().messages().list(
                userId='me',
                q=str(query.to_gmail_query()),
                maxResults=query.max_results
            ).execute()
            
            messages = []
            message_list = results.get('messages', [])
            
            if not message_list:
                print(f"No messages found for query: {str(query)}")
                return []
                
            for msg in message_list:
                # Get full message with format='full' to get all headers
                full_msg = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                
                # Create EmailMessage
                email = EmailMessage.from_gmail_message(full_msg)
                
                # Process if processor provided
                if processor:
                    processed = processor.process(email)
                    if processed:
                        email.html_content = processed
                        
                messages.append(email)
                
            return messages
            
        except Exception as e:
            print(f"Search failed: {str(e)}")
            raise GmailError(f"Search failed: {str(e)}")