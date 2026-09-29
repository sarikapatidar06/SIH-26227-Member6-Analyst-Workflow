from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "analyst_workflow.db"
DATA_DIR.mkdir(exist_ok=True)

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_conn()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS findings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        site_id TEXT NOT NULL,
        change_class TEXT NOT NULL,
        confidence REAL,
        summary TEXT,
        warnings TEXT,
        geometry_json TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        review_status TEXT NOT NULL DEFAULT 'PENDING',
        review_comment TEXT,
        reviewed_by TEXT,
        reviewed_at TEXT
    );

    CREATE TABLE IF NOT EXISTS observations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        finding_id INTEGER NOT NULL,
        observation_date TEXT NOT NULL,
        sensor TEXT,
        source_image TEXT,
        quality REAL,
        notes TEXT,
        FOREIGN KEY(finding_id) REFERENCES findings(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS provenance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        finding_id INTEGER NOT NULL,
        source TEXT,
        source_date TEXT,
        processing_steps TEXT,
        model_name TEXT,
        model_version TEXT,
        parameters TEXT,
        output_reference TEXT,
        FOREIGN KEY(finding_id) REFERENCES findings(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        finding_id INTEGER NOT NULL,
        action TEXT NOT NULL,
        actor TEXT NOT NULL,
        details TEXT,
        timestamp TEXT NOT NULL,
        FOREIGN KEY(finding_id) REFERENCES findings(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        finding_id INTEGER NOT NULL,
        feedback_type TEXT NOT NULL,
        comment TEXT,
        actor TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY(finding_id) REFERENCES findings(id) ON DELETE CASCADE
    );
    """)
    conn.commit()

    count = conn.execute("SELECT COUNT(*) AS c FROM findings").fetchone()["c"]
    if count == 0:
        import json
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()
        geometry = json.dumps({
            "type": "Polygon",
            "coordinates": [[[75.80, 22.70], [75.81, 22.70],
                             [75.81, 22.71], [75.80, 22.71],
                             [75.80, 22.70]]]
        })
        cur = conn.execute("""
            INSERT INTO findings
            (site_id, change_class, confidence, summary, warnings,
             geometry_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "DEMO-SITE-001",
            "Construction",
            0.91,
            "New built-up development detected between observations.",
            json.dumps(["Low cloud cover", "Alignment passed", "Persistence supported"]),
            geometry, now, now
        ))
        fid = cur.lastrowid

        observations = [
            ("2025-01-15", "Sentinel-2", "before_2025_01_15.tif", 0.96, "Baseline"),
            ("2025-06-20", "Sentinel-2", "middle_2025_06_20.tif", 0.94, "Construction emerging"),
            ("2025-10-12", "Sentinel-2", "after_2025_10_12.tif", 0.97, "Construction visible"),
        ]
        conn.executemany("""
            INSERT INTO observations
            (finding_id, observation_date, sensor, source_image, quality, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [(fid, *x) for x in observations])

        conn.execute("""
            INSERT INTO provenance
            (finding_id, source, source_date, processing_steps, model_name,
             model_version, parameters, output_reference)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            fid, "Local satellite catalogue", "2025-01-15 to 2025-10-12",
            "validation -> preprocessing -> registration -> tiling -> change analysis -> false-alarm checks",
            "team-change-model", "demo-1.0",
            json.dumps({"quality_threshold": 0.80, "persistence_required": True}),
            "local://demo/finding/1"
        ))

        conn.execute("""
            INSERT INTO audit_log (finding_id, action, actor, details, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (fid, "CREATED", "system", "Demo finding created", now))
        conn.commit()

    conn.close()
