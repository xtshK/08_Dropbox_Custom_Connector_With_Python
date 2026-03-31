from datetime import datetime
from fastapi import APIRouter, Depends
import dropbox
from dropbox.sharing import RequestedVisibility, SharedLinkSettings

from app.dependencies import get_dbx
from app.models.sharing import (
    CreateSharedLinkRequest,
    ListSharedLinksRequest,
    RevokeSharedLinkRequest,
    SharedLinkMetadata,
)

router = APIRouter(prefix="/sharing", tags=["Sharing"])

_VISIBILITY_MAP = {
    "public": RequestedVisibility.public,
    "team_only": RequestedVisibility.team_only,
    "password": RequestedVisibility.password,
}


def _to_response(link) -> SharedLinkMetadata:
    visibility = "unknown"
    if hasattr(link, "link_permissions") and hasattr(link.link_permissions, "resolved_visibility"):
        rv = link.link_permissions.resolved_visibility
        if rv is not None:
            visibility = rv.get_tag() if hasattr(rv, "get_tag") else str(rv)

    return SharedLinkMetadata(
        url=link.url,
        name=link.name,
        path_lower=link.path_lower or "",
        visibility=visibility,
        expires=link.expires.isoformat() if link.expires else None,
    )


@router.post(
    "/create-link",
    response_model=SharedLinkMetadata,
    summary="Create Shared Link",
    description="Create a shared link for a file or folder (including Team Folders).",
    operation_id="CreateSharedLink",
)
def create_shared_link(
    req: CreateSharedLinkRequest,
    dbx: dropbox.Dropbox = Depends(get_dbx),
):
    settings = SharedLinkSettings(
        requested_visibility=_VISIBILITY_MAP.get(req.requested_visibility, RequestedVisibility.public),
        link_password=req.password,
        expires=datetime.fromisoformat(req.expires) if req.expires else None,
    )
    try:
        link = dbx.sharing_create_shared_link_with_settings(req.path, settings)
    except dropbox.exceptions.ApiError as e:
        if "shared_link_already_exists" in str(e):
            links = dbx.sharing_list_shared_links(path=req.path, direct_only=True).links
            if links:
                return _to_response(links[0])
        raise
    return _to_response(link)


@router.post(
    "/list-links",
    response_model=list[SharedLinkMetadata],
    summary="List Shared Links",
    description="List shared links for a file or folder (including Team Folders).",
    operation_id="ListSharedLinks",
)
def list_shared_links(
    req: ListSharedLinksRequest,
    dbx: dropbox.Dropbox = Depends(get_dbx),
):
    result = dbx.sharing_list_shared_links(path=req.path, direct_only=True)
    return [_to_response(link) for link in result.links]


@router.post(
    "/revoke-link",
    summary="Revoke Shared Link",
    description="Revoke a shared link.",
    operation_id="RevokeSharedLink",
)
def revoke_shared_link(
    req: RevokeSharedLinkRequest,
    dbx: dropbox.Dropbox = Depends(get_dbx),
):
    dbx.sharing_revoke_shared_link(req.url)
    return {"status": "revoked", "url": req.url}
