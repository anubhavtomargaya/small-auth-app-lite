from typing import Optional
import base64
from .base import BaseProcessor

class TextProcessor(BaseProcessor):
    """Extract plain text content from emails"""
    
    def process(self, message: dict) -> Optional[str]:
        """Extract and decode plain text content"""
        try:
            payload = message.get('payload', {})
            text_part = self._get_payload_part(payload, 'text/plain')
            
            if text_part:
                content = self._extract_content(text_part)
                if content:
                    return self._decode_content(content)
            return None
            
        except Exception as e:
            self._logger.error(f"Text processing failed: {str(e)}")
            return None

    def _decode_content(self, content: str) -> str:
        """Decode base64 content to plain text"""
        try:
            data = content.replace("-", "+").replace("_", "/")
            decoded = base64.b64decode(data)
            return decoded.decode('utf-8')
        except Exception as e:
            self._logger.error(f"Content decoding failed: {str(e)}")
            return None
