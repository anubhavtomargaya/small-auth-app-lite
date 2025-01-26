from flask import current_app as app, jsonify, request, url_for, redirect
from . import gmail_bp
from sm_auth_app_lite.common.session_manager import (
    is_logged_in, get_auth_token, set_next_url
)
from sm_auth_app_lite.gmail_service.client import GmailClient
from sm_auth_app_lite.gmail_service.models.query import EmailQuery
from sm_auth_app_lite.gmail_service.models.credentials import GmailCredentials
from sm_auth_app_lite.blueprints.google_auth.routes import CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN_URI
from sm_auth_app_lite.gmail_service.processors.html import HTMLProcessor
from sm_auth_app_lite.gmail_service.processors.base import BaseProcessor
from sm_auth_app_lite.gmail_service.processors.regex import RegexProcessor
from datetime import datetime, timedelta

@gmail_bp.route('/', methods=['GET'])
def index():
    if not is_logged_in():
        set_next_url(url_for('gmail_bp.index'))
        app.logger.info("not logged in")
        return redirect(url_for('google_auth.login'))
    return "Use /search for emails or /recent for recent emails"

@gmail_bp.route('/search', methods=['GET'])
def search_emails():
    if not is_logged_in():
        return jsonify({"error": "Not authenticated"}), 401
        
    try:
        # Get token and create credentials
        oauth2_tokens = get_auth_token()
        credentials = {
            'token': oauth2_tokens['access_token'],
            'refresh_token': oauth2_tokens['refresh_token'],
            'token_uri': ACCESS_TOKEN_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'scopes': ['https://www.googleapis.com/auth/gmail.readonly']
        }
        
        gmail = GmailClient(GmailCredentials(**credentials))
        
        # Build query from params
        query = EmailQuery(
            sender=request.args.get('sender'),
            subject=request.args.get('subject'),
            after=datetime.now() - timedelta(days=int(request.args.get('days', 7))),
            max_results=int(request.args.get('max_results', 10))
        )
        
        # Search emails
        messages = gmail.search(query=query)
        return jsonify([{
            'id': msg.message_id,
            'subject': msg.subject,
            'sender': msg.sender,
            'date': msg.internal_date.isoformat() if msg.internal_date else None,
            'snippet': msg.snippet,
            'labels': msg.labels
        } for msg in messages])
        
    except Exception as e:
        app.logger.error(f"Search failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

def get_processor(processor_type: str = 'html'):
    """Get the appropriate processor based on type"""
    processors = {
        'html': HTMLProcessor(),
        'text': BaseProcessor(),
        'regex': RegexProcessor()
    }
    return processors.get(processor_type)

@gmail_bp.route('/recent', methods=['GET'])
def recent_emails():
    if not is_logged_in():
        return jsonify({"error": "Not authenticated"}), 401
        
    try:
        # Get token and create credentials
        oauth2_tokens = get_auth_token()
        credentials = {
            'token': oauth2_tokens['access_token'],
            'refresh_token': oauth2_tokens['refresh_token'],
            'token_uri': ACCESS_TOKEN_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'scopes': ['https://www.googleapis.com/auth/gmail.readonly']
        }
        
        gmail = GmailClient(GmailCredentials(**credentials))
        
        # Get parameters
        days = int(request.args.get('days', 7))
        max_results = int(request.args.get('max_results', 10))
        processor_type = request.args.get('processor', 'regex')
        
        # Get processor
        processor = get_processor(processor_type)
        if not processor:
            return jsonify({"error": f"Invalid processor type: {processor_type}"}), 400
        
        # Get recent messages
        messages = gmail.get_recent(days=days, max_results=max_results)
        
        # Process messages using the selected processor
        results = []
        for msg in messages:
            processed = processor.process(msg)
            if processed:
                results.append(processed)
                
        return jsonify(results)
        
    except Exception as e:
        app.logger.error(f"Recent emails failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

@gmail_bp.route('/hdfc', methods=['GET'])
def get_hdfc_transactions():
    if not is_logged_in():
        return jsonify({"error": "Not authenticated"}), 401
        
    try:
        # Get token and create credentials
        token = get_auth_token()
        credentials = GmailCredentials(**token)
        gmail = GmailClient(credentials)
        
        # Search HDFC emails
        query = EmailQuery(
            sender='alerts@hdfcbank.net',
            subject='UPI txn',
            after=datetime.now() - timedelta(days=int(request.args.get('days', 7))),
            max_results=int(request.args.get('max_results', 50))
        )
        
        messages = gmail.search(query=query)
        
        # Process HDFC emails
        processor = HTMLProcessor()
        
        results = []
        for msg in messages:
            try:
                result = processor.process(msg)
                if result:
                    results.append({
                        'message_id': msg.message_id,
                        'date': msg.internal_date.isoformat() if msg.internal_date else None,
                        'content': result
                    })
            except Exception as e:
                app.logger.error(f"Failed to process message {msg.message_id}: {str(e)}")
                continue
                
        return jsonify(results)
        
    except Exception as e:
        app.logger.error(f"HDFC processing failed: {str(e)}")
        return jsonify({"error": str(e)}), 500 