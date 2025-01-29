from typing import List, Dict, Optional, Set, Type, Union
from datetime import datetime
import logging

from .client import GmailClient
from .processors.base import BaseProcessor
from .models.message import EmailMessage
from .models.labels import GmailLabel
from .processors.html import HTMLProcessor
from .processors.regex import RegexProcessor
from .models.query import EmailQuery

from .exceptions import GmailServiceError

class GmailService:
    """Service layer for Gmail operations and message processing"""

    def __init__(
        self, 
        client: GmailClient, 
        processor: Union[BaseProcessor, Type[BaseProcessor], None] = None
    ):
        self.client = client
        # Initialize processor if class was passed
        self.processor = processor() if isinstance(processor, type) else processor
        self._logger = logging.getLogger(__name__)
        self._label_mapping = None  # Cache for label mapping

    @classmethod
    def with_processor(cls, client: GmailClient, processor_type: str = 'html') -> 'GmailService':
        """Factory method to create service with specific processor type"""
        processors = {
            'html': HTMLProcessor,
            'regex': RegexProcessor,
            'base': BaseProcessor,
            # Add more processors here
        }
        
        processor_class = processors.get(processor_type)
        if not processor_class:
            raise ValueError(f"Unknown processor type: {processor_type}")
            
        return cls(client, processor_class)

    def _get_label_mapping(self) -> Dict[str, str]:
        """Get or create mapping of label IDs to names"""
        if self._label_mapping is None:
            labels = self.get_labels()
            self._label_mapping = {label['id']: label['name'] for label in labels}
        return self._label_mapping

    def _process_messages(self, messages: List[EmailMessage]) -> List[Dict]:
        """Process a list of email messages using the configured processor"""
        label_mapping = self._get_label_mapping()
        
        def process_single_message(msg: EmailMessage) -> Optional[Dict]:
            try:
                if result := self.processor.process(msg):
                    return {
                        'message_id': msg.message_id,
                        'date': msg.internal_date.isoformat() if msg.internal_date else None,
                        'content': result,
                        'processor': self.processor.__class__.__name__,
                        'labels': [label_mapping.get(label_id, label_id) for label_id in msg.labels]
                    }
            except Exception as e:
                self._logger.error(f"Failed to process message {msg.message_id}: {str(e)}")
                return None

        return [
            result for msg in messages 
            if (result := process_single_message(msg))
        ]

    def get_recent_processed(
        self, 
        days: int = 7, 
        max_results: int = 10, 
        labels: Set[str] = {GmailLabel.INBOX.value}
    ) -> List[Dict]:
        """
        Get and process recent emails
        
        Args:
            days: Number of days to look back
            max_results: Maximum number of results to return
            labels: Set of Gmail labels to filter by
            
        Returns:
            List of processed email results
        """
        try:
            messages = self.client.get_recent(days=days, max_results=max_results, labels=labels)
            
            if not self.processor:
                label_mapping = self._get_label_mapping()
                return [{
                    **msg.to_dict(),
                    'labels': [label_mapping.get(label_id, label_id) for label_id in msg.labels]
                } for msg in messages]
            
            return self._process_messages(messages)
            
        except Exception as e:
            self._logger.error(f"Failed to get and process recent messages: {str(e)}")
            raise GmailServiceError(f"Service error: {str(e)}")

    def search_and_process(
        self, 
        query: EmailQuery,
        max_results: int = 50
    ) -> List[Dict]:
        """
        Search for and process emails matching the query
        
        Args:
            query: EmailQuery object containing search parameters
            max_results: Maximum number of results to return
            
        Returns:
            List of processed email results
        """
        try:
            messages = self.client.search(query=query, max_results=max_results)
            
            if not self.processor:
                self._logger.info("No processor, returning raw messages with label names")
                label_mapping = self._get_label_mapping()
                return [{
                    **msg.to_dict(),
                    'labels': [label_mapping.get(label_id, label_id) for label_id in msg.labels]
                } for msg in messages]
            
            return self._process_messages(messages)
            
        except Exception as e:
            self._logger.error(f"Failed to search and process messages: {str(e)}")
            raise GmailServiceError(f"Service error: {str(e)}")

    def get_labels(self) -> List[Dict[str, str]]:
        """
        Fetch and format all Gmail labels for the user
        
        Returns:
            List of dictionaries containing label information:
            [
                {
                    'id': 'INBOX',
                    'name': 'INBOX',
                    'type': 'system'  # or 'user' for custom labels
                },
                ...
            ]
        """
        try:
            # Fetch labels from Gmail API via client
            response = self.client.service.users().labels().list(userId='me').execute()
            labels = response.get('labels', [])
            
            formatted_labels = []
            for label in labels:
                formatted_labels.append({
                    'id': label['id'],
                    'name': label['name'],
                    'type': label['type'].lower(),
                    'messages_total': label.get('messagesTotal', 0),
                    'messages_unread': label.get('messagesUnread', 0)
                })
            
            self._logger.debug(f"Found {len(formatted_labels)} labels")
            return formatted_labels
            
        except Exception as e:
            self._logger.error(f"Failed to fetch labels: {str(e)}")
            raise GmailServiceError(f"Failed to fetch labels: {str(e)}") 