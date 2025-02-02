from typing import Dict, Any, Optional, List
import numpy as np
from sklearn.cluster import DBSCAN
import logging
from .html import HTMLProcessor
from ..models.message import EmailMessage
from ..services.openai_service import OpenAIService
from ..constants import DBSCAN_EPS, DBSCAN_MIN_SAMPLES, CATEGORY_MAPPING

class LLMProcessor(HTMLProcessor):
    """Process text using LLM embeddings and DBSCAN clustering after HTML processing"""
    
    def __init__(self):
        super().__init__()
        self._logger = logging.getLogger(__name__)
        self._openai_service = OpenAIService()
        self._embeddings_cache = []  # Store embeddings for clustering
        
    def process(self, message: EmailMessage) -> Optional[Dict[str, Any]]:
        """Override HTMLProcessor process to add LLM processing"""
        try:
            # First get HTML processing result
            html_result = super().process(message)
            if not html_result:
                return self._create_error_response(message, "HTML processing failed")

            # Get clean text from HTML processor's result
            clean_text = html_result['decoded_content'].get('text')
            if not clean_text:
                return self._create_error_response(message, "No text content found")

            # Create embedding but don't include in response
            try:
                embedding = self._openai_service.create_embedding(clean_text)
                
                # Store embedding internally for clustering
                self._store_embedding(message.message_id, embedding)
                
                html_result['decoded_content']['llm_analysis'] = {
                    'processed': True,
                    'category': None,  # Will be filled in by clustering service
                    'error': None
                }
                
            except Exception as e:
                self._logger.error(f"LLM processing failed for message {message.message_id}: {str(e)}")
                html_result['decoded_content']['llm_analysis'] = {
                    'processed': False,
                    'category': None,
                    'error': f'LLM processing failed: {str(e)}'
                }
            
            return html_result
            
        except Exception as e:
            return self._create_error_response(message, f"Processing failed: {str(e)}")

    def _store_embedding(self, message_id: str, embedding: List[float]):
        """Store embedding for later clustering"""
        if not hasattr(self, '_embeddings_store'):
            self._embeddings_store = {}
        self._embeddings_store[message_id] = embedding

    def _create_error_response(self, message: EmailMessage, error_msg: str) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            'metadata': message.to_dict(),
            'decoded_content': {
                'text': error_msg,
                'llm_analysis': {
                    'processed': False,
                    'category': None,
                    'error': error_msg
                }
            }
        } 