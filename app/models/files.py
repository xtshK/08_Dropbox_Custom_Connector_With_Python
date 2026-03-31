from pydantic import BaseModel, Field


class UploadRequest(BaseModel):
    path: str = Field(..., description="Dropbox path, e.g. /Team Folder/subfolder/file.txt", json_schema_extra={"x-ms-summary": "File Path"})
    mode: str = Field("add", description="Upload mode: add, overwrite, or update", json_schema_extra={"x-ms-summary": "Write Mode"})
    autorename: bool = Field(False, description="Auto-rename if file exists", json_schema_extra={"x-ms-summary": "Auto Rename"})


class DownloadRequest(BaseModel):
    path: str = Field(..., description="Dropbox path to download", json_schema_extra={"x-ms-summary": "File Path"})


class FileMetadata(BaseModel):
    id: str = Field(..., json_schema_extra={"x-ms-summary": "File ID"})
    name: str = Field(..., json_schema_extra={"x-ms-summary": "File Name"})
    path_display: str = Field(..., json_schema_extra={"x-ms-summary": "Display Path"})
    size: int = Field(..., json_schema_extra={"x-ms-summary": "Size (bytes)"})
    rev: str = Field(..., json_schema_extra={"x-ms-summary": "Revision"})
    server_modified: str = Field(..., json_schema_extra={"x-ms-summary": "Last Modified"})
