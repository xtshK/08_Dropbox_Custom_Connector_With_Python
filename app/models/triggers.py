from typing import Optional

from pydantic import BaseModel, Field


class FileChangeEntry(BaseModel):
    tag: str = Field(..., alias=".tag", description="file, folder, or deleted", json_schema_extra={"x-ms-summary": "Change Type"})
    id: Optional[str] = Field(None, json_schema_extra={"x-ms-summary": "ID"})
    name: str = Field(..., json_schema_extra={"x-ms-summary": "Name"})
    path_display: str = Field(..., json_schema_extra={"x-ms-summary": "Display Path"})
    size: Optional[int] = Field(None, json_schema_extra={"x-ms-summary": "Size (bytes)"})
    server_modified: Optional[str] = Field(None, json_schema_extra={"x-ms-summary": "Last Modified"})

    model_config = {"populate_by_name": True}
