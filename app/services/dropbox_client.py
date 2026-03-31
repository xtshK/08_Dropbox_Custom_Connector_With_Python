from typing import Optional

import dropbox
from dropbox.common import PathRoot

from app.config import settings

_root_namespace_id: Optional[str] = None


def _get_base_client() -> dropbox.Dropbox:
    return dropbox.Dropbox(
        oauth2_access_token="",
        oauth2_refresh_token=settings.dropbox_refresh_token,
        app_key=settings.dropbox_app_key,
        app_secret=settings.dropbox_app_secret,
    )


def _get_root_namespace_id(dbx: dropbox.Dropbox) -> str:
    global _root_namespace_id
    if _root_namespace_id is None:
        account = dbx.users_get_current_account()
        _root_namespace_id = account.root_info.root_namespace_id
    return _root_namespace_id


def get_dropbox_client() -> dropbox.Dropbox:
    """Return a Dropbox client rooted to the team namespace.

    This makes both personal folders and Team Folders accessible
    via normal path operations.
    """
    dbx = _get_base_client()
    root_ns_id = _get_root_namespace_id(dbx)
    dbx = dbx.with_path_root(PathRoot.root(root_ns_id))
    return dbx
