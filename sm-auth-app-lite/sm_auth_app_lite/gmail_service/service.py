from typing import List, Dict, Optional, Set, Type, Union
from datetime import datetime
import logging
import pandas as pd

from .client import GmailClient
from .processors.base import BaseProcessor
from .models.message import EmailMessage
from .models.labels import GmailLabel
from .processors.html import HTMLProcessor
from .processors.regex import RegexProcessor
from .models.query import EmailQuery
from .processors.llm_processor import LLMProcessor
from .exceptions import GmailServiceError
from .services.clustering_service import ClusteringService

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
        processor = cls._get_processor(processor_type)
        return cls(client, processor)

    @staticmethod
    def _get_processor(processor_type: str = 'html') -> BaseProcessor:
        """Get the appropriate processor based on type"""
        processors = {
            'html': HTMLProcessor(),
            'regex': RegexProcessor(), 
            'base': BaseProcessor(),
            'llm': LLMProcessor()
        }
        
        processor = processors.get(processor_type)
        if not processor:
            raise ValueError(f"Unknown processor type: {processor_type}")
            
        return processor
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
            
            # Use process_all_emails for LLMProcessor, otherwise use _process_messages
            if isinstance(self.processor, LLMProcessor):
                return self.process_all_emails(messages)
            else:
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

    def process_all_emails(self, emails: List[EmailMessage]) -> List[Dict]:
        """Process all emails and return processed results"""
        try:
            # Use the existing processor
            if not isinstance(self.processor, LLMProcessor):
                self._logger.warning("Processor is not LLMProcessor, switching to LLM processing")
                processor = LLMProcessor()
            else:
                processor = self.processor

            # Process all emails and create a list of dicts with necessary fields
            processed_data = []
            for email in emails:
                result = processor.process(email)
                if result:
                    processed_data.append({
                        'message_id': email.message_id,  # Get message_id from metadata
                        'date': email.internal_date.isoformat() if email.internal_date else None,
                        'content': result,
                        'processor': self.processor.__class__.__name__,
                        'labels': result.get('labels', [])
                    })

            # If no data was processed, return empty list
            if not processed_data:
                return []

            # Convert to DataFrame
            df = pd.DataFrame(processed_data)
            
            # Get embeddings from processor's store
            embeddings_dict = getattr(processor, '_embeddings_store', {})
            df['embedding'] = df['message_id'].map(embeddings_dict)

            # Remove rows where embedding failed
            df = df.dropna(subset=['embedding'])

            # Check if we have enough data for clustering
            if len(df) < 2:  # Need at least 2 points for meaningful clustering
                self._logger.warning("Not enough data for clustering, returning with default categories")
                return processed_data

            # Run clustering on complete dataset
            clustering_service = ClusteringService()
            df_with_categories = clustering_service.process_embeddings(df)

            # Drop embeddings column before returning results
            df_with_categories = df_with_categories.drop('embedding', axis=1)

            # Move category from top level to decoded_content
            results = []
            for record in df_with_categories.to_dict(orient='records'):
                category = record.pop('category', 'D')  # Remove category from top level
                record['content']['decoded_content']['category'] = category  # Put category in decoded_content
                results.append(record)

            return results
            
        except Exception as e:
            self._logger.error(f"Failed to process all emails: {str(e)}")
            raise GmailServiceError(f"Service error: {str(e)}") 