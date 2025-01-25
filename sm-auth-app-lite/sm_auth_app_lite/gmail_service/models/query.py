from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class EmailQuery:
    """Email search query parameters"""
    sender: Optional[str] = None
    subject: Optional[str] = None
    after: Optional[datetime] = None
    before: Optional[datetime] = None
    labels: Optional[List[str]] = None
    has_attachment: bool = False
    include_spam: bool = False
    max_results: int = 100
    raw_query: Optional[str] = None

    def to_gmail_query(self) -> str:
        """Convert to Gmail API query string"""
        parts = []
        
        if self.sender:
            parts.append(f"from:{self.sender}")
        
        if self.after:
            parts.append(f"after:{self.after.strftime('%Y/%m/%d')}")
            
        if self.before:
            parts.append(f"before:{self.before.strftime('%Y/%m/%d')}")
            
        if self.subject:
            parts.append(f"subject:{self.subject}")
            
        if self.has_attachment:
            parts.append("has:attachment")
            
        if not self.include_spam:
            parts.append("-in:spam")
            
        if self.raw_query:
            parts.append(self.raw_query)
            
        return " ".join(parts)
