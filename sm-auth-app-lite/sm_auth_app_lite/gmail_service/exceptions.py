class GmailServiceError(Exception):
    """Base exception for Gmail service errors"""
    pass

class AuthError(GmailServiceError):
    """Authentication related errors"""
    pass

class ProcessingError(GmailServiceError):
    """Content processing errors"""
    pass

class QueryError(GmailServiceError):
    """Query building or execution errors"""
    pass

class RateLimitError(GmailServiceError):
    """Gmail API rate limit exceeded"""
    pass 
class GmailError(GmailServiceError):
    """Gmail client errors"""
    pass 