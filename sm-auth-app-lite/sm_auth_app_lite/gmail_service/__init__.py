from .client import GmailClient
from .models.query import EmailQuery
from .models.message import EmailMessage
from .processors import HTMLProcessor, TextProcessor

__version__ = "0.1.0"

__all__ = [
    "GmailClient",
    "EmailQuery",
    "EmailMessage",
    "HTMLProcessor",
    "TextProcessor"
]
