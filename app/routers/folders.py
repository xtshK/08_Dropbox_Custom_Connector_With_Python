from fastapi import APIRouter, Depends
import dropbox
from dropbox.files import FolderMetadata as DbxFolderMeta, FileMetadata as DbxFileMeta

from app.dependencies import get_dbx
from app.models.folders import (
    CreateFolderRequest,
    DeleteFolderRequest,
    ListFolderRequest,
    FolderMetadata,
    EntryMetadata,
    ListFolderResponse,
)

router = APIRouter(prefix="/folders", tags=["Folders"])


@router.post(
    "/create",
    response_model=FolderMetadata,
    summary="Create Folder",
    description="Create a new folder in Dropbox (including Team Folders).",
    operation_id="CreateFolder",
)
def create_folder(
    req: CreateFolderRequest,
    dbx: dropbox.Dropbox = Depends(get_dbx),
):
    result = dbx.files_create_folder_v2(req.path)
    meta = result.metadata
    return FolderMetadata(
        id=meta.id,
        name=meta.name,
        path_display=meta.path_display,
    )


@router.post(
    "/delete",
    summary="Delete Folder",
    description="Delete a folder from Dropbox (including Team Folders).",
    operation_id="DeleteFolder",
)
def delete_folder(
    req: DeleteFolderRequest,
    dbx: dropbox.Dropbox = Depends(get_dbx),
):
    result = dbx.files_delete_v2(req.path)
    meta = result.metadata
    return {"name": meta.name, "path_display": meta.path_display}


@router.post(
    "/list",
    response_model=ListFolderResponse,
    summary="List Folder Contents",
    description="List contents of a folder in Dropbox (including Team Folders). Use empty string for root.",
    operation_id="ListFolder",
)
def list_folder(
    req: ListFolderRequest,
    dbx: dropbox.Dropbox = Depends(get_dbx),
):
    result = dbx.files_list_folder(
        req.path,
        recursive=req.recursive,
        limit=req.limit,
    )
    entries = []
    for entry in result.entries:
        e = {
            ".tag": "folder" if isinstance(entry, DbxFolderMeta) else "file",
            "id": entry.id,
            "name": entry.name,
            "path_display": entry.path_display,
        }
        if isinstance(entry, DbxFileMeta):
            e["size"] = entry.size
            e["server_modified"] = entry.server_modified.isoformat()
        entries.append(EntryMetadata(**e))

    return ListFolderResponse(
        entries=entries,
        has_more=result.has_more,
        cursor=result.cursor,
    )
