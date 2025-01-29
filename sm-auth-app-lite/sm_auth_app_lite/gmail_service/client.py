from typing import List, Optional, Union, Set, Dict, Any
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import logging

from .models.credentials import GmailCredentials
from .models.message import EmailMessage
from .models.query import EmailQuery
from .exceptions import GmailError, AuthError
from .models.labels import GmailLabel, LabelFilter

class GmailClient:
    """Gmail API client wrapper"""
    
    def __init__(self, credentials: GmailCredentials):
        self._validate_credentials(credentials)
        self.credentials = credentials
        self.service = self._build_service()
        self._logger = logging.getLogger(__name__)
        
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
            
    def get_recent(self, days: int = 7, max_results: int = 10, labels: Set[str] = {GmailLabel.INBOX.value}) -> List[EmailMessage]:
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
                self._logger.info("No recent messages found")
                return []
                
            cutoff_date = datetime.now() - timedelta(days=days) if days else None
            
            for msg in message_list:
                try:
                    # Get full message details
                    full_msg = self.service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='full'
                    ).execute()
                    
                    # Convert to EmailMessage
                    email = EmailMessage.from_gmail_message(full_msg)
                    
                    # Filter by date if needed
                    if cutoff_date and email.internal_date and email.internal_date < cutoff_date:
                        continue
                        
                    messages.append(email)
                    
                    # Check if we have enough messages after filtering
                    if len(messages) >= max_results:
                        break
                        
                except Exception as e:
                    self._logger.error(f"Failed to process message {msg['id']}: {str(e)}")
                    continue
                
            return messages
            
        except Exception as e:
            self._logger.error(f"Failed to get recent messages: {str(e)}")
            raise GmailError(f"Failed to get recent messages: {str(e)}")
        
    def search(self, query: EmailQuery = None, max_results: int = 10) -> List[EmailMessage]:
        """
        Search emails using Gmail query syntax
        """
        try:
            # Build Gmail query string
            q = self._build_search_query(query) if query else ""
            self._logger.debug(f"Search query: {q}")

            # Execute search
            response = self.service.users().messages().list(
                userId='me',
                q=q,
                maxResults=max_results
            ).execute()

            messages = []
            for msg in response.get('messages', []):
                try:
                    # Get full message details
                    full_msg = self.service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='full'
                    ).execute()
                    
                    # Extract required fields for EmailMessage
                    headers = {h['name']: h['value'] for h in full_msg['payload']['headers']}
                    
                    message = EmailMessage(
                        message_id=full_msg['id'],
                        thread_id=full_msg['threadId'],
                        internal_date=datetime.fromtimestamp(int(full_msg['internalDate'])/1000),
                        subject=headers.get('Subject', ''),
                        sender=headers.get('From', ''),
                        recipient=headers.get('To', ''),
                        snippet=full_msg.get('snippet', ''),
                        raw_message=full_msg,
                        labels=full_msg.get('labelIds', [])
                    )
                    messages.append(message)
                    
                except Exception as e:
                    self._logger.error(f"Failed to process message {msg['id']}: {str(e)}")
                    continue

            return messages

        except Exception as e:
            self._logger.error(f"Search failed: {str(e)}")
            return []

    def _build_search_query(self, query: EmailQuery) -> str:
        """Build Gmail API query string from EmailQuery object"""
        parts = []

        if query.sender:
            parts.append(f"from:{query.sender}")
        
        if query.subject:
            parts.append(f"subject:{query.subject}")

        if query.after:
            # Convert datetime to Gmail's search format (YYYY/MM/DD)
            after_str = query.after.strftime("%Y/%m/%d")
            parts.append(f"after:{after_str}")
            
        if query.before:
            before_str = query.before.strftime("%Y/%m/%d")
            parts.append(f"before:{before_str}")

        if query.labels:
            for label in query.labels:
                parts.append(f"label:{label}")

        if query.has_attachment:
            parts.append("has:attachment")

        return " ".join(parts)