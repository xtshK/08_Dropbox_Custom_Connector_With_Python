from urllib.parse import urlencode
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
import dropbox
from dropbox.files import FileMetadata as DbxFileMeta, DeletedMetadata

from app.dependencies import get_dbx

router = APIRouter(prefix="/triggers", tags=["Triggers"])


def _build_location_url(path: str, cursor: str, recursive: bool) -> str:
    params = urlencode({"path": path, "cursor": cursor, "recursive": str(recursive).lower()})
    return f"/triggers/file-changes?{params}"


@router.get(
    "/file-changes",
    summary="Monitor File Changes (Trigger)",
    description="Polling trigger that monitors a Dropbox folder (including Team Folders) for file changes.",
    operation_id="OnFileChanged",
    responses={
        200: {"description": "Changes detected"},
        202: {"description": "No changes, retry later"},
    },
)
def on_file_changed(
    path: str = Query(..., description="Folder path to monitor, e.g. /Team Folder"),
    cursor: str = Query(None, description="Cursor from previous poll (internal)"),
    recursive: bool = Query(True, description="Monitor subfolders"),
    dbx: dropbox.Dropbox = Depends(get_dbx),
):
    # First call: no cursor — initialize
    if not cursor:
        result = dbx.files_list_folder_get_latest_cursor(
            path, recursive=recursive
        )
        location = _build_location_url(path, result.cursor, recursive)
        return JSONResponse(
            status_code=202,
            content=None,
            headers={"Location": location, "Retry-After": "60"},
        )

    # Subsequent calls: check for changes
    result = dbx.files_list_folder_continue(cursor)
    new_location = _build_location_url(path, result.cursor, recursive)

    if not result.entries:
        return JSONResponse(
            status_code=202,
            content=None,
            headers={"Location": new_location, "Retry-After": "60"},
        )

    # Changes found
    changes = []
    for entry in result.entries:
        change = {
            "name": entry.name,
            "path_display": entry.path_display,
        }
        if isinstance(entry, DeletedMetadata):
            change[".tag"] = "deleted"
        elif isinstance(entry, DbxFileMeta):
            change[".tag"] = "file"
            change["id"] = entry.id
            change["size"] = entry.size
            change["server_modified"] = entry.server_modified.isoformat()
        else:
            change[".tag"] = "folder"
            change["id"] = entry.id
        changes.append(change)

    return JSONResponse(
        status_code=200,
        content=changes,
        headers={"Location": new_location},
    )
