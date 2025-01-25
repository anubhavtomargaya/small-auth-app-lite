from typing import Optional, Dict, Any
from bs4 import BeautifulSoup
from .base import BaseProcessor

class HTMLProcessor(BaseProcessor):
    """Process HTML emails with element targeting capabilities"""
    
    def __init__(self, target_element: Dict[str, str] = None):
        """Initialize with optional target element configuration"""
        super().__init__()
        self.target_element = target_element
        self.soup = None  # Store BeautifulSoup object

    def get_mime_type(self) -> str:
        return 'text/html'

    def process(self, message) -> Optional[Dict[str, Any]]:
        """Process email to extract metadata and HTML content"""
        try:
            # Get metadata and decoded content from base processor
            base_result = super().process(message)
            if not base_result or not base_result['decoded_content']:
                return None

            # Process HTML content and store soup
            self.soup = BeautifulSoup(base_result['decoded_content'], 'html.parser')
            
            # If no target specified, return full HTML
            if not self.target_element:
                base_result['decoded_content'] = {
                    'html': str(self.soup),
                    'text': self.soup.get_text(separator=' ', strip=True)
                }
                return base_result
            
            # Use find_elements method for target filtering
            elements = self.find_elements(self.target_element)
            if not elements:
                self._logger.warning(f"No elements found matching {self.target_element}")
                return None
                
            # Extract content from elements
            extracted = []
            for elem in elements:
                extracted.append({
                    'html': str(elem),
                    'text': elem.get_text(separator=' ', strip=True)
                })
                
            base_result['decoded_content'] = {
                'elements': extracted,
                'count': len(extracted)
            }
            return base_result
            
        except Exception as e:
            self._logger.error(f"HTML processing failed: {str(e)}")
            return None

    def find_elements(self, element_config: Dict[str, str]) -> list:
        """Find elements in the stored soup based on configuration"""
        if not self.soup:
            self._logger.warning("No HTML content has been processed yet")
            return []
            
        tag = element_config.get('tag')
        attrs = {k: v for k, v in element_config.items() if k != 'tag'}
        return self.soup.find_all(tag, attrs=attrs)
