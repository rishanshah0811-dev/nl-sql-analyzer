import os
import shutil
import tempfile
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

for key in ("GOOGLE_API_KEY",):
    if not os.environ.get(key):
        raise RuntimeError(f"Missing required environment variable: {key}")

from database import ingest_csv, get_schema_with_samples, DB_PATH, UPLOAD_DB_PATH
from claude_sql import nl_to_sql
from data_ingestion import build_sample_db

app = FastAPI(title="NL->SQL Analyzer", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Build sample DB if it doesn't exist."""
    if not DB_PATH.exists():
        print("[startup] Building sample database...")
        build_sample_db()
    else:
        print("[startup] Sample database found.")


class QueryRequest(BaseModel):
    question: str
    use_sample: bool = True


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/schema")
def get_schema(use_sample: bool = True):
    db = DB_PATH if use_sample else UPLOAD_DB_PATH
    if not db.exists():
        raise HTTPException(status_code=404, detail="Database not found. Upload a CSV first.")
    schema = get_schema_with_samples(db)
    return {"schema": schema}


@app.post("/query")
def query(req: QueryRequest):
    db = DB_PATH if req.use_sample else UPLOAD_DB_PATH
    if not db.exists():
        raise HTTPException(status_code=404, detail="Database not found.")
    result = nl_to_sql(req.question, db)
    return result


@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")
    suffix = Path(file.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)
    try:
        info = ingest_csv(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"CSV parse error: {e}")
    finally:
        tmp_path.unlink(missing_ok=True)
    return {"success": True, **info}


@app.delete("/upload")
def clear_upload():
    """Reset to sample dataset."""
    if UPLOAD_DB_PATH.exists():
        UPLOAD_DB_PATH.unlink()
    return {"success": True, "message": "Reverted to sample dataset."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
