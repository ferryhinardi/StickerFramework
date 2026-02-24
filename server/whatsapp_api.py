"""
WhatsApp Sticker Pack API Server.

Serves sticker pack metadata and images for the Android sticker app.
The app fetches packs from this server on startup, enabling dynamic
pack updates without publishing new app versions.

Endpoints:
    GET  /api/v1/packs                          -> List all available packs
    GET  /api/v1/packs/{pack_id}                -> Single pack metadata
    GET  /api/v1/packs/{pack_id}/stickers       -> List stickers in a pack
    GET  /api/v1/stickers/{pack_id}/{filename}  -> Download sticker image
    POST /api/v1/packs/{pack_id}/publish        -> Upload/update a pack

Run:
    uvicorn whatsapp_api:app --host 0.0.0.0 --port 8080
"""

import json
import os
import shutil
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, File, HTTPException, Header, UploadFile
from fastapi.responses import FileResponse

app = FastAPI(
    title="WhatsApp Sticker API",
    description="Serves sticker packs for the WhatsApp sticker Android app.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PACKS_DIR = Path(os.environ.get("STICKER_PACKS_DIR", "./sticker_packs"))
API_KEY = os.environ.get("WHATSAPP_API_KEY", "")  # empty = no auth required


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_pack_metadata(pack_id: str) -> dict:
    """Load and return the contents.json for a single pack."""
    # Validate pack_id to prevent path traversal
    if ".." in pack_id or "/" in pack_id or "\\" in pack_id:
        raise HTTPException(status_code=400, detail="Invalid pack_id")
    contents_path = PACKS_DIR / pack_id / "contents.json"
    if not contents_path.exists():
        raise HTTPException(status_code=404, detail=f"Pack '{pack_id}' not found")
    try:
        data = json.loads(contents_path.read_text())
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500, detail=f"Invalid contents.json for '{pack_id}'"
        )

    packs = data.get("sticker_packs", [])
    if not packs:
        raise HTTPException(status_code=500, detail=f"No sticker_packs in '{pack_id}'")
    return packs[0]


async def _verify_api_key(authorization: Optional[str] = Header(None)):
    """Simple bearer-token auth check (only when API_KEY is set)."""
    if not API_KEY:
        return  # No auth configured
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Missing or invalid Authorization header"
        )
    token = authorization.removeprefix("Bearer ").strip()
    if token != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/api/v1/packs")
async def list_packs():
    """Return metadata for all available sticker packs."""
    PACKS_DIR.mkdir(parents=True, exist_ok=True)
    packs = []
    for pack_path in sorted(PACKS_DIR.iterdir()):
        if not pack_path.is_dir():
            continue
        contents = pack_path / "contents.json"
        if not contents.exists():
            continue
        try:
            data = json.loads(contents.read_text())
            for p in data.get("sticker_packs", []):
                p["sticker_count"] = len(p.get("stickers", []))
                packs.append(p)
        except (json.JSONDecodeError, KeyError):
            continue
    return {"packs": packs}


@app.get("/api/v1/packs/{pack_id}")
async def get_pack(pack_id: str):
    """Return metadata for a single pack."""
    meta = _load_pack_metadata(pack_id)
    meta["sticker_count"] = len(meta.get("stickers", []))
    return meta


@app.get("/api/v1/packs/{pack_id}/stickers")
async def list_stickers(pack_id: str):
    """Return the stickers list for a pack."""
    meta = _load_pack_metadata(pack_id)
    return {"stickers": meta.get("stickers", [])}


@app.get("/api/v1/stickers/{pack_id}/{filename}")
async def get_sticker_image(pack_id: str, filename: str):
    """Serve a sticker or tray image file."""
    # Prevent path traversal
    if ".." in filename or "/" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    file_path = PACKS_DIR / pack_id / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {filename}")

    # Determine media type
    media_type = "image/webp"
    if filename.endswith(".png"):
        media_type = "image/png"

    return FileResponse(file_path, media_type=media_type)


@app.post("/api/v1/packs/{pack_id}/publish")
async def publish_pack(
    pack_id: str,
    contents: UploadFile = File(...),
    files: list[UploadFile] = File(default=[]),
    _auth=Depends(_verify_api_key),
):
    """
    Upload/update a sticker pack.

    Expects multipart form data:
        - contents: the contents.json file
        - files: sticker image files + tray icon
    """
    # Validate pack_id to prevent path traversal
    if ".." in pack_id or "/" in pack_id or "\\" in pack_id:
        raise HTTPException(status_code=400, detail="Invalid pack_id")

    ALLOWED_CONTENT_TYPES = {"image/webp", "image/png"}

    pack_dir = PACKS_DIR / pack_id
    pack_dir.mkdir(parents=True, exist_ok=True)

    # Save contents.json
    contents_data = await contents.read()
    try:
        json.loads(contents_data)  # Validate JSON
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid contents.json")
    (pack_dir / "contents.json").write_bytes(contents_data)

    # Save sticker/tray files
    saved_files = []
    for upload_file in files:
        if not upload_file.filename:
            continue
        # Validate content type
        if (
            upload_file.content_type
            and upload_file.content_type not in ALLOWED_CONTENT_TYPES
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid content type '{upload_file.content_type}' for {upload_file.filename}. "
                f"Allowed: {', '.join(sorted(ALLOWED_CONTENT_TYPES))}",
            )
        # Prevent path traversal
        safe_name = Path(upload_file.filename).name
        if ".." in safe_name:
            continue
        dest = pack_dir / safe_name
        data = await upload_file.read()
        dest.write_bytes(data)
        saved_files.append(safe_name)

    return {
        "status": "ok",
        "pack_id": pack_id,
        "files_saved": len(saved_files) + 1,  # +1 for contents.json
    }


# ---------------------------------------------------------------------------
# Health / info
# ---------------------------------------------------------------------------


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "WhatsApp Sticker API",
        "version": "1.0.0",
        "docs": "/docs",
    }
