# SIH 2026 — Analyst Workflow & Export

## Semantic Retrieval and Multi-Temporal Change Analysis of Satellite Imagery

**Problem Statement:** SIH 2026 — PS 26227  
**Team:** ALGOSPHERE_  
**Module:** Member 6 — Analyst Workflow + Export

### Overview

This module implements the analyst-side workflow for reviewing and documenting satellite change-detection findings.

It connects AI-generated change results with an auditable analyst verification and reporting workflow.

### Features

- Confirm / Reject / Uncertain analyst review
- Analyst comments and feedback
- Multi-temporal observation timeline
- Evidence and provenance tracking
- Audit log for analyst actions
- Change signal and evidence-level reporting
- CSV export
- GeoJSON export
- HTML report export
- PDF report export
- SQLite database persistence
- FastAPI REST APIs

### Analyst Workflow

```text
Change Detection Result
        ↓
Finding Summary
        ↓
Timeline & Evidence
        ↓
Analyst Verification
        ↓
Confirm / Reject / Uncertain
        ↓
Audit Log + Feedback
        ↓
Provenance
        ↓
CSV / GeoJSON / HTML / PDF Export
