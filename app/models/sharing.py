from typing import Optional

from pydantic import BaseModel, Field


class CreateSharedLinkRequest(BaseModel):
    path: str = Field(..., description="File or folder path", json_schema_extra={"x-ms-summary": "Path"})
    requested_visibility: str = Field("public", description="public, team_only, or password", json_schema_extra={"x-ms-summary": "Visibility"})
    password: Optional[str] = Field(None, description="Password for the link (if visibility=password)", json_schema_extra={"x-ms-summary": "Password"})
    expires: Optional[str] = Field(None, description="Expiry date in ISO format", json_schema_extra={"x-ms-summary": "Expires"})


class ListSharedLinksRequest(BaseModel):
    path: str = Field(..., description="File or folder path", json_schema_extra={"x-ms-summary": "Path"})


class RevokeSharedLinkRequest(BaseModel):
    url: str = Field(..., description="Shared link URL to revoke", json_schema_extra={"x-ms-summary": "Shared Link URL"})


class SharedLinkMetadata(BaseModel):
    url: str = Field(..., json_schema_extra={"x-ms-summary": "URL"})
    name: str = Field(..., json_schema_extra={"x-ms-summary": "Name"})
    path_lower: str = Field(..., json_schema_extra={"x-ms-summary": "Path"})
    visibility: str = Field(..., json_schema_extra={"x-ms-summary": "Visibility"})
    expires: Optional[str] = Field(None, json_schema_extra={"x-ms-summary": "Expires"})
