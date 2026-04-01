from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import dropbox

from app.routers import auth, files, folders, search, triggers

app = FastAPI(
    title="Dropbox Business Connector",
    description="Custom Connector for Power Automate — Dropbox Business with Team Folder support",
    version="1.0.0",
)

# Register routers
app.include_router(auth.router)
app.include_router(files.router)
app.include_router(folders.router)
app.include_router(search.router)
app.include_router(triggers.router)


# --- Global Dropbox exception handlers ---

@app.exception_handler(dropbox.exceptions.AuthError)
async def auth_error_handler(request: Request, exc: dropbox.exceptions.AuthError):
    return JSONResponse(status_code=401, content={"error_code": "auth_error", "message": "Dropbox authentication failed. Token may be expired or invalid."})


@app.exception_handler(dropbox.exceptions.BadInputError)
async def bad_input_handler(request: Request, exc: dropbox.exceptions.BadInputError):
    return JSONResponse(status_code=400, content={"error_code": "bad_input", "message": str(exc)})


@app.exception_handler(dropbox.exceptions.ApiError)
async def api_error_handler(request: Request, exc: dropbox.exceptions.ApiError):
    error_str = str(exc.error) if exc.error else str(exc)

    if "not_found" in error_str:
        return JSONResponse(status_code=404, content={"error_code": "not_found", "message": "File or folder not found.", "detail": error_str})
    if "no_permission" in error_str or "insufficient_permissions" in error_str:
        return JSONResponse(status_code=403, content={"error_code": "no_permission", "message": "No permission to access this resource.", "detail": error_str})
    if "conflict" in error_str:
        return JSONResponse(status_code=409, content={"error_code": "conflict", "message": "Write conflict.", "detail": error_str})
    if "insufficient_space" in error_str:
        return JSONResponse(status_code=507, content={"error_code": "insufficient_space", "message": "Dropbox storage quota exceeded.", "detail": error_str})

    return JSONResponse(status_code=500, content={"error_code": "dropbox_api_error", "message": "Dropbox API error.", "detail": error_str})


@app.exception_handler(dropbox.exceptions.RateLimitError)
async def rate_limit_handler(request: Request, exc: dropbox.exceptions.RateLimitError):
    retry_after = exc.backoff if hasattr(exc, "backoff") else 30
    return JSONResponse(
        status_code=429,
        content={"error_code": "rate_limit", "message": f"Rate limited. Retry after {retry_after}s."},
        headers={"Retry-After": str(retry_after)},
    )


@app.get("/", tags=["Root"])
def root():
    return {"service": "Dropbox Business Connector", "version": "1.0.0", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    from app.config import settings

    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=True)
