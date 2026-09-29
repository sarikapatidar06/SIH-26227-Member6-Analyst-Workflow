from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from .database import init_db, get_conn
from .schemas import ReviewRequest, FeedbackRequest, CreateFindingRequest
from .services import (
    get_full,
    review_finding,
    add_feedback,
    export_finding,
    create_finding,
)

app = FastAPI(
    title="SIH 26227 — Member 6 Analyst Workflow API",
    version="1.0.0"
)

# Ensure the local SQLite schema exists for both normal runs and tests.
init_db()

@app.on_event("startup")
def startup():
    init_db()

@app.get("/api/health")
def health():
    return {"status": "ok", "module": "member6-analyst-workflow"}

@app.get("/api/findings")
def list_findings():
    conn = get_conn()
    rows = conn.execute("""
        SELECT id, site_id, change_class, confidence, review_status,
               reviewed_by, reviewed_at, updated_at
        FROM findings ORDER BY updated_at DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]
@app.post("/api/findings")
def create_new_finding(payload: CreateFindingRequest):
    result = create_finding(
        site_id=payload.site_id,
        change_class=payload.change_class,
        summary=payload.summary,
        warnings=payload.warnings,
        change_signal=payload.change_signal,
        evidence_level=payload.evidence_level,
        before_date=payload.before_date,
        after_date=payload.after_date,
        before_image=payload.before_image,
        after_image=payload.after_image,
        detection_evidence=payload.detection_evidence,
        provenance_source=payload.provenance_source,
    )
    return {"message": "Finding created", **result}

@app.get("/api/findings/{finding_id}")
def finding(finding_id: int):
    conn = get_conn()
    result = get_full(conn, finding_id)
    conn.close()
    if not result:
        raise HTTPException(404, "Finding not found")
    return result

@app.get("/api/timeline/{finding_id}")
def timeline(finding_id: int):
    conn = get_conn()
    result = get_full(conn, finding_id)
    conn.close()
    if not result:
        raise HTTPException(404, "Finding not found")
    return result["timeline"]

@app.get("/api/provenance/{finding_id}")
def provenance(finding_id: int):
    conn = get_conn()
    result = get_full(conn, finding_id)
    conn.close()
    if not result:
        raise HTTPException(404, "Finding not found")
    return result["provenance"]

@app.get("/api/audit/{finding_id}")
def audit(finding_id: int):
    conn = get_conn()
    result = get_full(conn, finding_id)
    conn.close()
    if not result:
        raise HTTPException(404, "Finding not found")
    return result["audit_log"]

@app.post("/api/findings/{finding_id}/review")
def review(finding_id: int, payload: ReviewRequest):
    result = review_finding(
        finding_id, payload.decision, payload.comment, payload.analyst
    )
    if not result:
        raise HTTPException(404, "Finding not found")
    return {"message": "Review saved", **result}

@app.post("/api/findings/{finding_id}/feedback")
def feedback(finding_id: int, payload: FeedbackRequest):
    result = add_feedback(
        finding_id, payload.feedback_type, payload.comment, payload.actor
    )
    if not result:
        raise HTTPException(404, "Finding not found")
    return {"message": "Feedback saved", **result}

@app.get("/api/export/{finding_id}")
def export(finding_id: int, format: str = "html"):
    if format not in {"csv", "geojson", "html", "pdf"}:
        raise HTTPException(400, "format must be csv, geojson, html or pdf")
    path = export_finding(finding_id, format)
    if not path:
        raise HTTPException(404, "Finding not found")
    media = {
        "csv": "text/csv",
        "geojson": "application/geo+json",
        "html": "text/html",
        "pdf": "application/pdf",
    }[format]
    return FileResponse(path, media_type=media, filename=path.name)
