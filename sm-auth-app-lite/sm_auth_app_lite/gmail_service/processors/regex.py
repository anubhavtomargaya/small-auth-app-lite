from typing import Dict, Any
import re
import logging

class RegexProcessor:
    """Process text using regex patterns from external configuration"""
    
    def __init__(self):
        self._logger = logging.getLogger(__name__)

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