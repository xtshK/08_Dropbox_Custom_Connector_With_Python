from fastapi import APIRouter, Depends
import dropbox
from dropbox.files import SearchV2Arg, SearchOptions, FileMetadata as DbxFileMeta

from app.dependencies import get_dbx
from app.models.search import SearchRequest, SearchMatchMetadata, SearchResponse

router = APIRouter(prefix="/search", tags=["Search"])


@router.post(
    "/files",
    response_model=SearchResponse,
    summary="Search Files",
    description="Search for files and folders across personal and Team Folders.",
    operation_id="SearchFiles",
)
def search_files(
    req: SearchRequest,
    dbx: dropbox.Dropbox = Depends(get_dbx),
):
    options = SearchOptions(
        path=req.path if req.path else None,
        max_results=req.max_results,
        file_extensions=req.file_extensions,
    )
    result = dbx.files_search_v2(req.query, options=options)

    matches = []
    for match in result.matches:
        metadata = match.metadata.get_metadata()
        is_file = isinstance(metadata, DbxFileMeta)
        matches.append(SearchMatchMetadata(
            id=metadata.id,
            name=metadata.name,
            path_display=metadata.path_display,
            tag="file" if is_file else "folder",
            size=metadata.size if is_file else None,
            server_modified=metadata.server_modified.isoformat() if is_file else None,
        ))

    return SearchResponse(
        matches=matches,
        has_more=result.has_more,
    )
