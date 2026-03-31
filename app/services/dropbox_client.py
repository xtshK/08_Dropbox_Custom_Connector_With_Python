from typing import Dict, Optional

import dropbox
from dropbox.common import PathRoot

from app.config import settings

# Cache root_namespace_id per access token to avoid repeated API calls
_ns_cache: Dict[str, str] = {}


def _get_root_namespace_id(dbx: dropbox.Dropbox, cache_key: str) -> str:
    if cache_key not in _ns_cache:
        account = dbx.users_get_current_account()
        _ns_cache[cache_key] = account.root_info.root_namespace_id
    return _ns_cache[cache_key]


def get_dropbox_client(access_token: Optional[str] = None) -> dropbox.Dropbox:
    """Return a Dropbox client rooted to the team namespace.

    Args:
        access_token: OAuth2 access token from the user's Authorization header.
                      If None, falls back to the configured refresh token (single-user mode).

    This makes both personal folders and Team Folders accessible
    via normal path operations.
    """
    if access_token:
        # Multi-user mode: use the per-user access token from Power Automate
        dbx = dropbox.Dropbox(oauth2_access_token=access_token)
        cache_key = access_token[:16]  # Use prefix as cache key
    else:
        # Single-user fallback: use the configured refresh token
        dbx = dropbox.Dropbox(
            oauth2_access_token="",
            oauth2_refresh_token=settings.dropbox_refresh_token,
            app_key=settings.dropbox_app_key,
            app_secret=settings.dropbox_app_secret,
        )
        cache_key = "default"

    root_ns_id = _get_root_namespace_id(dbx, cache_key)
    dbx = dbx.with_path_root(PathRoot.root(root_ns_id))
    return dbx
