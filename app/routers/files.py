import io
from fastapi import APIRouter, Depends, Form
from fastapi.responses import StreamingResponse
import dropbox

from app.dependencies import get_dbx

router = APIRouter(prefix="/files", tags=["Files"])


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
