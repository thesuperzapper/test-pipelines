import logging
import os
import json
import base64
import hashlib
import sys
import time

from requests_oauthlib import OAuth2Session
import requests

#########################################################################################
# Constants
#########################################################################################
ISSUER_URL = "https://deploykf.example.com:8443/dex"
CLIENT_ID = "kubeflow-pipelines-sdk"
REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"
SCOPE = ["openid", "email", "groups", "profile", "offline_access"]
CREDENTIALS_PATH = os.path.join(
    os.path.expanduser("~"), ".config", "kfp", "credentials.json"
)
HTTP_TIMEOUT = 15
SKIP_TLS_VERIFY = True


#########################################################################################
# Logging
#########################################################################################
logger = logging.getLogger(__name__)
logger.propagate = False
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    fmt="%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


####################################################################################################
# Helpers
####################################################################################################
def _create_pkce_verifier() -> (str, str):
    """
    Create a PKCE code verifier and its derived challenge.

    See https://tools.ietf.org/html/rfc7636#section-4.1
    """
    # Generate a code_verifier of length between 43 and 128 characters
    code_verifier = base64.urlsafe_b64encode(os.urandom(96)).decode("utf-8")
    code_verifier = code_verifier.rstrip("=")
    code_verifier = code_verifier[:128]

    # Generate the code_challenge using the S256 method
    sha256_digest = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = base64.urlsafe_b64encode(sha256_digest).decode("utf-8").rstrip("=")

    return code_verifier, code_challenge


def _write_credentials(issuer: str, token: str) -> None:
    """Write credentials to the JSON file."""

    # Create the directory, if it doesn't exist
    credential_dir = os.path.dirname(CREDENTIALS_PATH)
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir, exist_ok=True)

    # Read all existing credentials from the JSON file
    data = {}
    if os.path.exists(CREDENTIALS_PATH):
        with open(CREDENTIALS_PATH, "r") as file:
            data = json.load(file)

    # Update the credentials for the given issuer
    data[issuer] = token
    logger.info("Writing credentials to: %s", CREDENTIALS_PATH)
    with open(CREDENTIALS_PATH, "w") as file:
        json.dump(data, file)


def _read_credentials(issuer: str) -> dict:
    """Read credentials from the JSON file."""
    logger.info("Checking for existing credentials in: %s", CREDENTIALS_PATH)
    if os.path.exists(CREDENTIALS_PATH):
        with open(CREDENTIALS_PATH, "r") as file:
            data = json.load(file)
            return data.get(issuer, {})
    return {}


def _fetch_openid_configuration(issuer) -> dict:
    """Fetches OIDC configuration from the issuer's well-known endpoint."""
    well_known_endpoint = f"{issuer}/.well-known/openid-configuration"
    logger.info("Fetching OpenID configuration from: %s", well_known_endpoint)
    response = requests.get(well_known_endpoint, verify=not SKIP_TLS_VERIFY)
    response.raise_for_status()
    return response.json()


def get_token():
    """Get a JWT token for the configured issuer."""

    # Fetch the OpenID Connect configuration
    config = _fetch_openid_configuration(ISSUER_URL)
    issuer = config["issuer"]
    token_endpoint = config["token_endpoint"]
    authorization_endpoint = config["authorization_endpoint"]

    # Return the current token, if it's valid for at least 5 more minutes
    stored_token = _read_credentials(issuer)
    if stored_token:
        expires_at = stored_token.get("expires_at", 0)
        expires_in = expires_at - time.time()
        logger.info("Found existing token which expires in %d seconds", expires_in)
        if expires_in > 300:
            return stored_token["id_token"]

    # Create an OAuth2Session
    oauth = OAuth2Session(
        CLIENT_ID,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        token=stored_token,
    )

    # Attempt to refresh the token
    new_token = None
    if "refresh_token" in stored_token:
        logger.warning("Attempting to refresh token...")
        try:
            new_token = oauth.refresh_token(
                token_endpoint,
                client_id=CLIENT_ID,
                timeout=HTTP_TIMEOUT,
                verify=not SKIP_TLS_VERIFY,
            )
        except Exception as ex:
            logger.error("Failed to refresh token!", exc_info=ex)

    # If refresh succeeded, return the new token
    if new_token:
        logger.info("Successfully refreshed token!")
        _write_credentials(issuer, new_token)
        return new_token["id_token"]

    # Start the authorization flow
    logger.info("Starting new authorization flow...")
    verifier, challenge = _create_pkce_verifier()
    authorization_url, state = oauth.authorization_url(
        authorization_endpoint,
        code_challenge_method="S256",
        code_challenge=challenge,
    )

    # ensure everything is printed to the console before continuing
    sys.stderr.flush()
    time.sleep(0.5)

    # Get the authorization code from the user
    print(
        f"\nPlease open this URL in a browser to continue:\n > {authorization_url}\n",
        flush=True,
    )
    user_input = input("Enter the authorization code:\n > ")
    authorization_code = user_input.strip()

    # Exchange the authorization code for a token
    new_token = oauth.fetch_token(
        token_endpoint,
        code=authorization_code,
        code_verifier=verifier,
        include_client_id=True,
        state=state,
        timeout=HTTP_TIMEOUT,
        verify=not SKIP_TLS_VERIFY,
    )
    logger.info("Successfully fetched new token!")
    _write_credentials(issuer, new_token)
    return new_token["id_token"]


####################################################################################################
# Main
####################################################################################################
def main():
    # Disable TLS verification, if needed
    if SKIP_TLS_VERIFY:
        requests.packages.urllib3.disable_warnings()
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    # Get the JWT token
    jwt_token = get_token()
    logger.info("Value of current JWT:\n\n %s\n", jwt_token)


main()
