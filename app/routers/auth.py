from fastapi import APIRouter, Depends
import dropbox

from app.dependencies import get_dbx

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get(
    "/test",
    summary="Test Connection",
    description="Verify that the Dropbox connection is working and Team Folder access is available.",
    operation_id="TestConnection",
)
def test_connection(dbx: dropbox.Dropbox = Depends(get_dbx)):
    account = dbx.users_get_current_account()
    root_info = account.root_info
    return {
        "status": "connected",
        "account_id": account.account_id,
        "display_name": account.name.display_name,
        "email": account.email,
        "root_namespace_id": root_info.root_namespace_id,
        "home_namespace_id": root_info.home_namespace_id,
        "is_team_account": hasattr(root_info, "home_path"),
    }
