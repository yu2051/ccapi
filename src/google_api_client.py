# src/google_api_client.py
import base64
import json
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from src.config import get_gemini_config_by_id

def get_credentials(account_id: str):
    """
    Loads credentials from the specified Gemini configuration.
    """
    config = get_gemini_config_by_id(account_id)
    if not config:
        raise ValueError(f"Configuration for account '{account_id}' not found.")

    creds_json = base64.b64decode(config['credentials']).decode('utf-8')
    creds_info = json.loads(creds_json)
    
    credentials = Credentials.from_service_account_info(
        creds_info,
        scopes=['https://www.googleapis.com/auth/cloud-platform']
    )
    
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        
    return credentials, config['project']
