from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, List

@dataclass
class EmailMessage:
    """Represents a processed email message"""
    message_id: str
    thread_id: str
    internal_date: datetime
    subject: Optional[str]
    sender: Optional[str]
    recipient: Optional[str]
    snippet: str
    raw_message: Dict
    labels: List[str]
    
    @classmethod
    def from_gmail_message(cls, message: Dict) -> 'EmailMessage':
        """Create EmailMessage from Gmail API response"""
        headers = message.get('payload', {}).get('headers', [])
        
        return cls(
            message_id=message['id'],
            thread_id=message['threadId'],
            internal_date=datetime.fromtimestamp(
                int(message['internalDate'])/1000
            ),
            subject=next(
                (h['value'] for h in headers 
                 if h['name'].lower() == 'subject'),
                None
            ),
            sender=next(
                (h['value'] for h in headers 
                 if h['name'].lower() == 'from'),
                None
            ),
            recipient=next(
                (h['value'] for h in headers 
                 if h['name'].lower() == 'to'),
                None
            ),
            snippet=message.get('snippet', ''),
            raw_message=message,
            labels=message.get('labelIds', [])
        )

    def to_dict(self) -> Dict:
        """Convert EmailMessage to dictionary"""
        return {
            'message_id': self.message_id,
            'thread_id': self.thread_id,
            'date': self.internal_date.isoformat() if self.internal_date else None,
            'subject': self.subject,
            'sender': self.sender,
            'recipient': self.recipient,
            'snippet': self.snippet,
            'labels': self.labels
        }
