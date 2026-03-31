from typing import List, Optional

from pydantic import BaseModel, Field


class CreateFolderRequest(BaseModel):
    path: str = Field(..., description="Folder path to create, e.g. /Team Folder/new-folder", json_schema_extra={"x-ms-summary": "Folder Path"})


class DeleteFolderRequest(BaseModel):
    path: str = Field(..., description="Folder path to delete", json_schema_extra={"x-ms-summary": "Folder Path"})


class ListFolderRequest(BaseModel):
    path: str = Field("", description="Folder path to list (empty string for root)", json_schema_extra={"x-ms-summary": "Folder Path"})
    recursive: bool = Field(False, description="List recursively", json_schema_extra={"x-ms-summary": "Recursive"})
    limit: int = Field(100, description="Max entries to return", ge=1, le=2000, json_schema_extra={"x-ms-summary": "Limit"})


class FolderMetadata(BaseModel):
    id: str = Field(..., json_schema_extra={"x-ms-summary": "Folder ID"})
    name: str = Field(..., json_schema_extra={"x-ms-summary": "Folder Name"})
    path_display: str = Field(..., json_schema_extra={"x-ms-summary": "Display Path"})


class EntryMetadata(BaseModel):
    tag: str = Field(..., alias=".tag", description="file or folder", json_schema_extra={"x-ms-summary": "Type"})
    id: str = Field(..., json_schema_extra={"x-ms-summary": "ID"})
    name: str = Field(..., json_schema_extra={"x-ms-summary": "Name"})
    path_display: str = Field(..., json_schema_extra={"x-ms-summary": "Display Path"})
    size: Optional[int] = Field(None, json_schema_extra={"x-ms-summary": "Size (bytes)"})
    server_modified: Optional[str] = Field(None, json_schema_extra={"x-ms-summary": "Last Modified"})

    model_config = {"populate_by_name": True}


class ListFolderResponse(BaseModel):
    entries: List[EntryMetadata]
    has_more: bool = Field(..., json_schema_extra={"x-ms-summary": "Has More"})
    cursor: str = Field(..., json_schema_extra={"x-ms-summary": "Cursor"})
