from typing import Dict, Any, Optional
import re
import logging
from .html import HTMLProcessor
from ..models.message import EmailMessage

hdfc_patterns = {
    "amount": r"Rs\.(\d+\.\d{2})",
    "vpa": r"to VPA\s+([^\s]+)",
    "recipient": r"@\w+\s+([A-Za-z\s]+?)\s+on",
    "date": r"on\s+(\d{2}-\d{2}-\d{2})",
    "reference": r"reference number is (\d+)"
}

class RegexProcessor(HTMLProcessor):
    """Process text using regex patterns after HTML processing"""
    
    def __init__(self):
        super().__init__()
        self._patterns = hdfc_patterns

    def process(self, message: EmailMessage) -> Optional[Dict[str, Any]]:
        """Override HTMLProcessor process to add regex extraction"""
        try:
            # First get HTML processing result
            html_result = super().process(message)
            if not html_result:
                self._logger.warning(f"HTML processing failed for message {message.message_id}")
                return {
                    'metadata': message.to_dict(),
                    'decoded_content': {
                        'text': 'HTML processing failed',
                        'extracted': {'data': {k: None for k in self._patterns.keys()},
                                    'error': 'HTML processing failed'
                                    }
                    }
                }

            # Get clean text from HTML processor's result
            clean_text = html_result['decoded_content'].get('text')
            if not clean_text:
                self._logger.warning(f"No clean text found in HTML result for message {message.message_id}")
                html_result['decoded_content']['extracted'] = {
                    'data': {k: None for k in self._patterns.keys()},
                    'error': 'No text content found'
                }
                return html_result

            # Apply regex patterns on clean text
            try:
                extracted = self.extract(clean_text, self._patterns)
                html_result['decoded_content']['extracted'] = {
                    'data': extracted,
                    'error': None
                }
                
                # Add processing status
                if not any(extracted.values()):
                    html_result['decoded_content']['extracted']['error'] = 'No patterns matched'
                else:
                    html_result['decoded_content']['extracted']['error'] = None
                    
            except Exception as e:
                self._logger.error(f"Pattern extraction failed for message {message.message_id}: {str(e)}")
                html_result['decoded_content']['extracted'] = {
                    'data': {k: None for k in self._patterns.keys()},
                    'error': f'Pattern extraction failed: {str(e)}'
                }
            
            return html_result
            
        except Exception as e:
            self._logger.error(f"Regex processing failed completely for message {message.message_id}: {str(e)}")
            return {
                'metadata': message.to_dict(),
                'decoded_content': {
                    'text': 'Processing failed',
                    'extracted': {
                        'data': {k: None for k in self._patterns.keys()},
                        'error': f'Processing failed: {str(e)}'
                    }
                }
            }

    def extract(self, text: str, patterns: Dict[str, str]) -> Dict[str, Any]:
        """Extract data using provided regex patterns"""
        results = {}
        for field_name, pattern in patterns.items():
            try:
                match = re.search(pattern, text)
                results[field_name] = match.group(1) if match else None
                if not match:
                    self._logger.debug(f"No match found for {field_name} using pattern: {pattern}")
            except Exception as e:
                self._logger.error(f"Pattern matching failed for {field_name}: {str(e)}")
                results[field_name] = None
                
        return results 