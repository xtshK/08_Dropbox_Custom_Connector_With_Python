import io
from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.responses import StreamingResponse
import dropbox
from dropbox.files import WriteMode

from app.dependencies import get_dbx
from app.models.files import FileMetadata

router = APIRouter(prefix="/files", tags=["Files"])

UPLOAD_SESSION_THRESHOLD = 150 * 1024 * 1024  # 150MB


def _write_mode(mode: str) -> WriteMode:
    if mode == "overwrite":
        return WriteMode.overwrite
    elif mode == "update":
        return WriteMode.overwrite  # simplified; update requires rev
    return WriteMode.add


@router.post(
    "/upload",
    response_model=FileMetadata,
    summary="Upload File",
    description="Upload a file to Dropbox (including Team Folders). Max 150MB per request.",
    operation_id="UploadFile",
)
def upload_file(
    path: str = Form(..., description="Dropbox destination path, e.g. /Team Folder/file.txt"),
    mode: str = Form("add", description="Write mode: add, overwrite"),
    autorename: bool = Form(False, description="Auto-rename if exists"),
    file: UploadFile = File(..., description="File to upload"),
    dbx: dropbox.Dropbox = Depends(get_dbx),
):
    content = file.file.read()
    meta = dbx.files_upload(
        content,
        path,
        mode=_write_mode(mode),
        autorename=autorename,
    )
    return FileMetadata(
        id=meta.id,
        name=meta.name,
        path_display=meta.path_display,
        size=meta.size,
        rev=meta.rev,
        server_modified=meta.server_modified.isoformat(),
    )


@router.post(
    "/download",
    summary="Download File",
    description="Download a file from Dropbox (including Team Folders).",
    operation_id="DownloadFile",
    responses={200: {"content": {"application/octet-stream": {}}}},
)
def download_file(
    path: str = Form(..., description="Dropbox file path to download"),
    dbx: dropbox.Dropbox = Depends(get_dbx),
):
    meta, response = dbx.files_download(path)
    return StreamingResponse(
        io.BytesIO(response.content),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{meta.name}"',
            "X-Dropbox-Path": meta.path_display,
            "X-Dropbox-Rev": meta.rev,
            "X-Dropbox-Size": str(meta.size),
        },
    )
