from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import logging
import base64
from ..models.message import EmailMessage
from ..exceptions import ProcessingError

class BaseProcessor(ABC):
    """Base processor that extracts and decodes email content"""
    
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)

    def process(self, message: EmailMessage) -> Optional[Dict[str, Any]]:
        """Process email to extract metadata and decoded content
        
        Returns:
            Dict containing:
                - metadata: Dict of email metadata
                - decoded_content: UTF-8 decoded content if found
        """
        try:
            # Step 1: Extract metadata and raw content
            extracted = self._extract_raw_content(message)
            if not extracted:
                return None
                
            # Step 2: Decode content if present
            decoded = self._decode_content(extracted['encoded_content']) if extracted['encoded_content'] else None
            #check mime type and process accordingly; add metadata for it later.
            return {
                'metadata': extracted['metadata'],
                'decoded_content': {
                    'html': decoded
                }
            }
            
        except Exception as e:
            self._logger.error(f"Processing failed: {str(e)}")
            raise ProcessingError(f"Processing failed: {str(e)}")

    def _extract_raw_content(self, message: EmailMessage) -> Optional[Dict[str, Any]]:
        """Extract metadata and encoded content from email"""
        try:
            # Get metadata
            metadata = {
                'message_id': message.message_id,
                'thread_id': message.thread_id,
                'date': message.internal_date.isoformat(),
                'subject': message.subject,
                'sender': message.sender,
                'recipient': message.recipient,
                'labels': message.labels
            }
            
            # Get encoded content
            payload = message.raw_message.get('payload', {})
            content_part = self._get_payload_part(payload, self.get_mime_type())
            encoded_content = self._extract_content(content_part) if content_part else None
            
            return {
                'metadata': metadata,
                'encoded_content': encoded_content
            }
            
        except Exception as e:
            self._logger.error(f"Content extraction failed: {str(e)}")
            return None

    def _decode_content(self, encoded_content: str) -> Optional[str]:
        """Decode base64 content to UTF-8"""
        try:
            if not encoded_content:
                return None
                
            # Handle base64 padding and decode
            padded = encoded_content.replace("-", "+").replace("_", "/")
            decoded = base64.b64decode(padded)
            return decoded.decode('utf-8')
            
        except Exception as e:
            self._logger.error(f"Content decoding failed: {str(e)}")
            return None

    @abstractmethod
    def get_mime_type(self) -> str:
        """Return mime type this processor handles"""
        pass

    def get_mime_type(self) -> str:
        return 'text/html'

    def _get_payload_part(self, payload: Dict, mime_type: str) -> Optional[Dict]:
        """Find payload part with specific mime type"""
        if not payload:
            return None
            
        if payload.get('mimeType') == mime_type:
            return payload
            
        for part in payload.get('parts', []):
            found = self._get_payload_part(part, mime_type)
            if found:
                return found
        return None

    def _extract_content(self, part: Dict) -> Optional[str]:
        """Extract encoded content from payload part"""
        if not part or 'body' not in part:
            return None
            
        body = part['body']
        return body.get('data')
