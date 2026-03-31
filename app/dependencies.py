from typing import Optional

import dropbox
from fastapi import Header

from app.services.dropbox_client import get_dropbox_client


def get_dbx(authorization: Optional[str] = Header(None)) -> dropbox.Dropbox:
    """Extract Bearer token from Authorization header if present.

    - With token: multi-user mode (each user's own Dropbox)
    - Without token: single-user fallback (configured refresh token)
    """
    access_token = None
    if authorization and authorization.startswith("Bearer "):
        access_token = authorization[7:]  # Strip "Bearer " prefix

    return get_dropbox_client(access_token)
