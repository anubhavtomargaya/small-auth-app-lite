from enum import Enum, auto
from typing import List, Set

class GmailLabel(Enum):
    """Gmail system labels"""
    # System labels
    INBOX = 'INBOX'
    SENT = 'SENT'
    DRAFT = 'DRAFT'
    TRASH = 'TRASH'
    SPAM = 'SPAM'
    STARRED = 'STARRED'
    UNREAD = 'UNREAD'
    
    # Category labels
    CATEGORY_PERSONAL = 'CATEGORY_PERSONAL'
    CATEGORY_SOCIAL = 'CATEGORY_SOCIAL'
    CATEGORY_PROMOTIONS = 'CATEGORY_PROMOTIONS'
    CATEGORY_UPDATES = 'CATEGORY_UPDATES'
    CATEGORY_FORUMS = 'CATEGORY_FORUMS'
    
    @classmethod
    def category_labels(cls) -> Set[str]:
        """Get all category labels"""
        return {
            label.value for label in cls 
            if label.value.startswith('CATEGORY_')
        }
    
    @classmethod
    def system_labels(cls) -> Set[str]:
        """Get all system labels"""
        return {
            label.value for label in cls 
            if not label.value.startswith('CATEGORY_')
        }

class LabelFilter:
    """Helper class for label filtering operations"""
    
    @staticmethod
    def has_any_label(message_labels: List[str], target_labels: Set[str]) -> bool:
        """Check if message has any of the target labels"""
        return bool(set(message_labels) & target_labels)
    
    @staticmethod
    def has_all_labels(message_labels: List[str], target_labels: Set[str]) -> bool:
        """Check if message has all target labels"""
        return set(target_labels).issubset(set(message_labels)) 