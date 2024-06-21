import asyncio
from concurrent.futures import Executor
import os.path

from google.auth.credentials import Credentials
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials as ServiceCredentials
from google.oauth2.credentials import Credentials as OAuthCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
import logging


def _get_oauth_credentials(scopes: list[str]) -> Credentials:
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = OAuthCredentials.from_authorized_user_file("token.json", scopes)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


def _get_service_credentials(scopes: list[str]) -> ServiceCredentials:
    return ServiceCredentials.from_service_account_file(
        "service_account_key.json",
        scopes=scopes,
    )


def get_credentials(scopes: list[str]) -> Credentials | None:
    """Get credentials from service account or oauth.
    
    Args:
        scopes: a list of permission scopes.
        
    Returns:
        the credentials if found, otherwise, None
    """
    if os.path.exists("credentials.json"):
        logging.info("Found Oauth2 account file.")
        return _get_oauth_credentials(scopes)

    if os.path.exists("service_account_key.json"):
        logging.info("Found service account file.")
        return _get_service_credentials(scopes)

    return None
