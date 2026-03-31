from typing import List, Optional

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query string", json_schema_extra={"x-ms-summary": "Query"})
    path: str = Field("", description="Restrict search to this folder path", json_schema_extra={"x-ms-summary": "Folder Path"})
    max_results: int = Field(20, description="Max results to return", ge=1, le=100, json_schema_extra={"x-ms-summary": "Max Results"})
    file_extensions: Optional[List[str]] = Field(None, description="Filter by file extensions, e.g. ['pdf','docx']", json_schema_extra={"x-ms-summary": "File Extensions"})


class SearchMatchMetadata(BaseModel):
    id: str = Field(..., json_schema_extra={"x-ms-summary": "ID"})
    name: str = Field(..., json_schema_extra={"x-ms-summary": "Name"})
    path_display: str = Field(..., json_schema_extra={"x-ms-summary": "Display Path"})
    tag: str = Field(..., description="file or folder", json_schema_extra={"x-ms-summary": "Type"})
    size: Optional[int] = Field(None, json_schema_extra={"x-ms-summary": "Size (bytes)"})
    server_modified: Optional[str] = Field(None, json_schema_extra={"x-ms-summary": "Last Modified"})


class SearchResponse(BaseModel):
    matches: List[SearchMatchMetadata]
    has_more: bool = Field(..., json_schema_extra={"x-ms-summary": "Has More"})
