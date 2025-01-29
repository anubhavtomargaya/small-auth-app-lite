from flask import current_app as app, jsonify, request, url_for, redirect, send_file, send_from_directory, render_template
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
from sm_auth_app_lite.gmail_service.service import GmailService
from typing import Optional
import os

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
        # Get processor type from request args, default to None for raw messages
        processor_type = request.args.get('processor')
        service = get_gmail_service(processor_type=processor_type)
        
        query = EmailQuery(
            sender=request.args.get('sender'),
            subject=request.args.get('subject'),
            after=datetime.now() - timedelta(days=int(request.args.get('days', 7))),
            max_results=int(request.args.get('max_results', 10))
        )
        
        results = service.search_and_process(query=query)
        return jsonify(results)
        
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

def get_gmail_service(processor_type: Optional[str] = None) -> GmailService:
    """Helper to create GmailService with credentials and processor"""
    oauth2_tokens = get_auth_token()
    credentials = {
        'token': oauth2_tokens['access_token'],
        'refresh_token': oauth2_tokens['refresh_token'],
        'token_uri': ACCESS_TOKEN_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'scopes': ['https://www.googleapis.com/auth/gmail.readonly']
    }
    
    client = GmailClient(GmailCredentials(**credentials))
    
    if processor_type:
        return GmailService.with_processor(client, processor_type)
    return GmailService(client)

@gmail_bp.route('/hdfc', methods=['GET'])
def get_hdfc_transactions():
    if not is_logged_in():
        return jsonify({"error": "Not authenticated"}), 401
        
    try:
        # Use HTML processor for HDFC emails
        service = get_gmail_service(processor_type='html')
        
        query = EmailQuery(
            sender='alerts@hdfcbank.net',
            subject='UPI txn',
            after=datetime.now() - timedelta(days=int(request.args.get('days', 7))),
            max_results=int(request.args.get('max_results', 50))
        )
        
        results = service.search_and_process(query=query)
        return jsonify(results)
        
    except Exception as e:
        app.logger.error(f"HDFC processing failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

@gmail_bp.route('/recent', methods=['GET'])
def recent_emails():
    if not is_logged_in():
        return jsonify({"error": "Not authenticated"}), 401
        
    try:
        # Get processor type from request args, default to regex
        processor_type = request.args.get('processor', 'regex')
        service = get_gmail_service(processor_type=processor_type)
        
        results = service.get_recent_processed(
            days=int(request.args.get('days', 7)),
            max_results=int(request.args.get('max_results', 10))
        )
        return jsonify(results)
        
    except Exception as e:
        app.logger.error(f"Recent emails failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

@gmail_bp.route('/labels', methods=['GET'])
def get_labels():
    if not is_logged_in():
        return jsonify({"error": "Not authenticated"}), 401
        
    try:
        service = get_gmail_service()  # No processor needed for labels
        labels = service.get_labels()
        return jsonify(labels)
        
    except Exception as e:
        app.logger.error(f"Failed to get labels: {str(e)}")
        return jsonify({"error": str(e)}), 500

