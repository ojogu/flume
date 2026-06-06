from fastapi import Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.oauth2 import id_token
from google.auth.transport import requests
import os
from src.utils.config import config
from src.core.exception_base import ServerError
from src.utils.log import get_logger

logger = get_logger(__name__)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


class GoogleAuthService:
    SCOPES = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ]
    CLIENT_ID = config.client_id
    CLIENT_SECRET = config.client_secret
    REDIRECT_URI = config.redirect_url

    @property
    def _client_config(self):
        return {
            "web": {
                "client_id": self.CLIENT_ID,
                "client_secret": self.CLIENT_SECRET,
                "redirect_uris": [self.REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }

    def login_with_google(self):
        try:
            logger.info("Initializing OAuth flow for Google authentication.")
            flow = Flow.from_client_config(
                self._client_config,
                scopes=self.SCOPES,
                redirect_uri=self.REDIRECT_URI,
                autogenerate_code_verifier=False,
            )
            auth_url, state = flow.authorization_url(
                access_type="offline",
                include_granted_scopes="true",
                prompt="consent",
            )
            logger.info(f"Generated Google OAuth authorization URL: {auth_url}")
            redirect_response = RedirectResponse(auth_url)
            redirect_response.set_cookie(
                key="oauth_state",
                value=state,
                httponly=True,
                secure=True,
                samesite="Lax",
            )
            return auth_url
        except Exception as e:
            logger.exception(
                f"Error generating Google OAuth authorization URL: {e}"
            )
            raise ServerError()

    def handle_callback(self, request: Request):
        try:
            logger.info(f"cookies, {request.cookies}")

            flow = Flow.from_client_config(
                self._client_config,
                scopes=self.SCOPES,
                redirect_uri=self.REDIRECT_URI,
                state=request.query_params.get("state"),
                autogenerate_code_verifier=False,
            )

            authorization_response = str(request.url)
            flow.fetch_token(authorization_response=authorization_response)
            credentials = flow.credentials

            logger.info("OAuth callback handled successfully")
            cred = {
                "access_token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "id_token": credentials.id_token,
            }
            logger.info("cred generated")
            return cred
        except Exception as e:
            logger.exception("Error handling OAuth callback: %s", e)
            raise ServerError()

    def verify_id(self, id_code):
        info = id_token.verify_oauth2_token(
            id_code,
            requests.Request(),
            self.CLIENT_ID,
            clock_skew_in_seconds=10,
        )
        logger.info("info generated")
        return info

    @staticmethod
    def refresh_credentials(
        access_token, refresh_token, client_id, client_secret, scopes
    ):
        creds = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=scopes,
        )
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return creds


