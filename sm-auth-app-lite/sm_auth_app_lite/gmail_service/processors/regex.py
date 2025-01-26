from typing import Dict, Any, Optional
import re
import logging
from .base import BaseProcessor
from ..models.message import EmailMessage
hdfc_patterns = {
    "amount": r"Rs\.(\d+\.\d{2})",
    "vpa": r"to VPA\s+([^\s]+)",
    "recipient": r"@\w+\s+([A-Za-z\s]+?)\s+on",  # Updated to handle mixed case names
    "date": r"on\s+(\d{2}-\d{2}-\d{2})",
    "reference": r"reference number is (\d+)"
}
class RegexProcessor(BaseProcessor):
    """Process text using regex patterns from external configuration"""
    
    def __init__(self):
        super().__init__()
        self._patterns =hdfc_patterns

    def get_mime_type(self) -> str:
        return 'text/html'  # We'll process HTML content

    def process(self, message: EmailMessage) -> Optional[Dict[str, Any]]:
        """Override base process to add regex extraction"""
        # First get base processing result
        base_result = super().process(message)
        if not base_result:
            return None

        # Then apply regex extraction on decoded content
        if base_result['decoded_content']:
            extracted = self.extract(base_result['decoded_content'], self._patterns)
            return {
                'metadata': base_result['metadata'],
                'decoded_content': base_result['decoded_content'],
                'extracted': extracted
            }
        return base_result

    def extract(self, text: str, patterns: Dict[str, str]) -> Dict[str, Any]:
        """
        Extract data using provided regex patterns
        
        Args:
            text: Text to process
            patterns: Dict mapping field names to regex patterns
                     e.g. {"amount": r"Rs\.?\s*(\d+(?:\.\d{2})?)", 
                           "date": r"(\d{2}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})"}
        
        Returns:
            Dict with extracted values
        """
        try:
            results = {}
            for field_name, pattern in patterns.items():
                match = re.search(pattern, text)
                if match:
                    # Always use first capture group
                    results[field_name] = match.group(1)
                else:
                    results[field_name] = None
                    self._logger.debug(f"No match found for {field_name} using pattern: {pattern}")

            return results

        except Exception as e:
            self._logger.error(f"Extraction failed: {str(e)}")
            return {} 