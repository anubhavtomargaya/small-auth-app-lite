from typing import List, Optional, Union, Set
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from .models.credentials import GmailCredentials
from .models.message import EmailMessage
from .models.query import EmailQuery
from .exceptions import GmailError, AuthError
from .processors.base import BaseProcessor
from .models.labels import GmailLabel, LabelFilter

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
            
    def get_recent(self, days: int = 7, max_results: int = 10,labels: Set[str] = {GmailLabel.INBOX.value}) -> List[EmailMessage]:
        """Get recent emails using direct messages.list API"""
        try:
            # Get messages directly using messages.list
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results,
                labelIds=list(labels) if labels else None
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
                
                # Check if we have enough messages after filtering
                if len(messages) >= max_results:
                    break
                    
            return messages
            
        except Exception as e:
            print(f"Failed to get recent messages: {str(e)}")
            raise GmailError(f"Failed to get recent messages: {str(e)}")
        
    def search(
        self, 
        query: EmailQuery, 
        processor: Optional[BaseProcessor] = None,
        include_labels: Set[str] = {GmailLabel.INBOX.value},
        exclude_labels: Set[str] = None
    ) -> List[EmailMessage]:
        """
        Search emails with query
        
        Args:
            query: EmailQuery object with search criteria
            processor: Optional processor for email content
            include_labels: Set of labels that messages must have (default: INBOX)
            exclude_labels: Set of labels to exclude (default: all category labels)
        """
        try:
            # Set default exclude labels if none provided
            if exclude_labels is None:
                exclude_labels = GmailLabel.category_labels()
            
            # Execute search
            results = self.service.users().messages().list(
                userId='me',
                q=str(query.to_gmail_query()),
                maxResults=query.max_results,
                labelIds=list(include_labels)
            ).execute()
            
            messages = []
            message_list = results.get('messages', [])
            
            if not message_list:
                print(f"No messages found for query: {str(query)}")
                return []
                
            for msg in message_list:
                # Get full message details
                full_msg = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                
                # Check message labels
                msg_labels = full_msg.get('labelIds', [])
                
                # Skip if message has any excluded labels
                if exclude_labels and LabelFilter.has_any_label(msg_labels, exclude_labels):
                    continue
                    
                # Skip if message doesn't have all required labels
                if include_labels and not LabelFilter.has_all_labels(msg_labels, include_labels):
                    continue
                
                # Create EmailMessage
                email = EmailMessage.from_gmail_message(full_msg)
                
                # Process if processor provided
                if processor:
                    processed = processor.process(email)
                    if processed:
                        email.html_content = processed
                        
                messages.append(email)
                
                # Check if we have enough messages after filtering
                if len(messages) >= query.max_results:
                    break
                    
            return messages
            
        except Exception as e:
            print(f"Search failed: {str(e)}")
            raise GmailError(f"Search failed: {str(e)}")