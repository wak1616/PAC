import os
import msal
import requests
from dotenv import load_dotenv
import logging
from datetime import datetime

# Set up logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sharepoint_download.log'),
        logging.StreamHandler()
    ]
)

def acquire_token():
    """Get an access token for Microsoft Graph API using MSAL"""
    load_dotenv()
    tenant_id = os.getenv('SHAREPOINT_TENANT_ID')
    client_id = os.getenv('SHAREPOINT_CLIENT_ID')
    client_secret = os.getenv('SHAREPOINT_CLIENT_SECRET')
    
    # Log everything for troubleshooting
    logging.info(f"Using tenant ID: {tenant_id}")
    logging.info(f"Using client ID: {client_id}")
    # Don't log the full secret for security reasons
    logging.info(f"Client secret present: {bool(client_secret)}")
    
    # Validate presence of credentials
    if not all([tenant_id, client_id, client_secret]):
        raise ValueError("Missing one or more Azure AD app credentials (TENANT_ID, CLIENT_ID, CLIENT_SECRET) in environment variables.")
    
    # Create MSAL app
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    app = msal.ConfidentialClientApplication(
        client_id=client_id,
        authority=authority,
        client_credential=client_secret
    )
    
    # Get token for Microsoft Graph API
    scopes = ["https://graph.microsoft.com/.default"]
    
    result = app.acquire_token_for_client(scopes=scopes)
    
    # Log token result (without the actual token)
    if "access_token" in result:
        token_length = len(result["access_token"])
        logging.info(f"Acquired token successfully (length: {token_length})")
    else:
        error = result.get("error", "unknown_error")
        error_description = result.get("error_description", "No error description")
        logging.error(f"Failed to acquire token: {error} - {error_description}")
        raise Exception(f"Could not acquire access token: {error} - {error_description}")
    
    return result["access_token"]

def download_sharepoint_file():
    """Test simplified Graph API access"""
    try:
        # Get access token
        logging.info("Starting authentication process")
        access_token = acquire_token()
        
        # Set up headers for Graph API requests
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        
        # Test a simple Graph API call to get the current user to verify the token works
        test_url = "https://graph.microsoft.com/v1.0/me"
        logging.info(f"Testing Graph API token with call to: {test_url}")
        test_response = requests.get(test_url, headers=headers)
        
        logging.info(f"Test response status code: {test_response.status_code}")
        if test_response.status_code != 200:
            logging.error(f"Error in test call: {test_response.text}")
            # Continue anyway - this might fail if using app permissions
        
        # Try a simple call to SharePoint to check permissions
        site_domain = "useyecorp.sharepoint.com"
        logging.info(f"Getting site information for {site_domain}")
        site_url = f"https://graph.microsoft.com/v1.0/sites/{site_domain}:/"
        site_response = requests.get(site_url, headers=headers)
        
        logging.info(f"Site response status code: {site_response.status_code}")
        if site_response.status_code != 200:
            logging.error(f"Error getting site: {site_response.text}")
            raise Exception(f"Failed to access SharePoint site. Status code: {site_response.status_code}, Response: {site_response.text}")
        
        site_data = site_response.json()
        logging.info(f"Site information retrieved successfully: {site_data.get('displayName')}")
        
        # Output the first level of SharePoint site data for debugging
        for key, value in site_data.items():
            if isinstance(value, (str, int, bool, float)) or value is None:
                logging.info(f"Site data - {key}: {value}")
        
        logging.info("Authentication and basic API access successful")
        return True
        
    except Exception as e:
        logging.error(f"Error in Graph API access: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    download_sharepoint_file() 