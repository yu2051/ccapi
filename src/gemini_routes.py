# src/gemini_routes.py
import json
import logging
from fastapi import APIRouter, Request, Response, Depends, HTTPException, Header, Body
from src.config import get_gemini_config_by_id
from src.google_api_client import get_credentials

# Assuming these functions are defined elsewhere, based on the original file
# If they are not, you might need to move them here or adjust the imports
# from .google_api_client import send_gemini_request, build_gemini_payload_from_native
# from .config import SUPPORTED_MODELS

# Placeholder for functions that were in the original file but not provided in context
# You should replace these with your actual implementation
def send_gemini_request(payload, is_streaming, credentials):
    # This is a placeholder. Implement your logic to send requests to Google's API.
    logging.warning("send_gemini_request is a placeholder and has not been implemented.")
    return Response(content=json.dumps({"placeholder_response": "send_gemini_request not implemented"}), media_type="application/json")

def build_gemini_payload_from_native(request, model):
    logging.warning("build_gemini_payload_from_native is a placeholder.")
    return {}

SUPPORTED_MODELS = [] # Placeholder

router = APIRouter()

# Dependency to verify password for a given account ID
async def verify_gemini_password(x_account_id: str = Header(...), request: Request = None):
    config = get_gemini_config_by_id(x_account_id)
    if not config:
        raise HTTPException(status_code=400, detail=f"Invalid X-Account-ID: {x_account_id}")
    
    # Extract password from the request body
    password = None
    if request:
        try:
            body = await request.json()
            password = body.get("password") # Assuming password is in the body
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON body")

    # In some cases, the password might not be in the body, handle as needed
    # For this example, we assume it's required and check it.
    if not password or config.get('password') != password:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid password")
        
    return True

@router.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def gemini_proxy(request: Request, full_path: str, x_account_id: str = Header(..., alias="X-Account-ID")):
    """
    Native Gemini API proxy endpoint.
    Handles all native Gemini API calls by proxying them directly to Google's API.
    """
    try:
        # First, get the correct credentials for the account
        credentials, project_id = get_credentials(x_account_id)

        # Get the request body
        post_data = await request.body()
        
        is_streaming = "stream" in full_path.lower()
        model_name = _extract_model_from_path(full_path)
        
        logging.info(f"Gemini proxy request for account '{x_account_id}': path={full_path}, model={model_name}")
        
        if not model_name:
            raise HTTPException(status_code=400, detail="Could not extract model name from path")

        incoming_request = json.loads(post_data) if post_data else {}
        gemini_payload = build_gemini_payload_from_native(incoming_request, model_name)
        
        # Pass credentials to the request function
        response = send_gemini_request(gemini_payload, is_streaming=is_streaming, credentials=credentials)
        
        return response
        
    except ValueError as e:
        # Catches the error from get_credentials if account_id is not found
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Gemini proxy error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Proxy error: {str(e)}")

def _extract_model_from_path(path: str) -> str:
    """Extract the model name from a Gemini API path."""
    try:
        parts = path.split('/')
        models_index = parts.index('models')
        if models_index + 1 < len(parts):
            model_name = parts[models_index + 1]
            return model_name.split(':')[0]
    except (ValueError, IndexError):
        return None

# You may need to re-implement these or adjust them based on the new auth flow
@router.get("/v1/models")
async def list_models(x_account_id: str = Header(..., alias="X-Account-ID")):
    # This endpoint might need to be adapted to return models based on the account
    return {"models": SUPPORTED_MODELS}

@router.get("/health")
async def health_check():
    return {"status": "healthy"}
