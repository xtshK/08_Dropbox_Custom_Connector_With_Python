import dropbox
from app.services.dropbox_client import get_dropbox_client


def get_dbx() -> dropbox.Dropbox:
    return get_dropbox_client()
