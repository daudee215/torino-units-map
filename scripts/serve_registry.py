"""Local-only review ledger. Run alongside the existing static server on 8765.

No company data or remote database. Writes require an exact allowed local Origin,
an approved Host and JSON, and can only append decisions for existing candidates.
"""
from datetime import date, datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import sqlite3
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "output/registry/properties.sqlite"
ORIGINS = {"http://127.0.0.1:8765", "http://localhost:8765"}


class Handler(BaseHTTPRequestHandler):
    def trusted_host(self):
        return self.headers.get("Host") in {"127.0.0.1:8766", "localhost:8766"}

    def answer(self, status, value):
        payload = json.dumps(value,ensure_ascii=False,allow_nan=False).encode("utf-8")
        self.send_response(status)
        origin = self.headers.get("Origin")
        if origin in ORIGINS:
            self.send_header("Access-Control-Allow-Origin",origin)
            self.send_header("Vary","Origin")
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Cache-Control","no-store")
        self.send_header("X-Content-Type-Options","nosniff")
        self.send_header("Content-Length",str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self):
        if not self.trusted_host() or self.headers.get("Origin") not in ORIGINS:
            return self.answer(403,{"error":"Unapproved local origin or host"})
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin",self.headers["Origin"])
        self.send_header("Access-Control-Allow-Methods","GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers","Content-Type")
        self.send_header("Vary","Origin")
        self.end_headers()

    def do_GET(self):
        if not self.trusted_host():
            return self.answer(403,{"error":"Unapproved host"})
        path = urlparse(self.path).path
        if not DB.exists():
            return self.answer(503,{"error":"Registry has not been built"})
        if path == "/api/health":
            with sqlite3.connect(DB) as db:
                count = db.execute("SELECT COUNT(*) FROM review_events").fetchone()[0]
            return self.answer(200,{"status":"ok","storage":"local_sqlite","review_events":count})
        match = re.fullmatch(r"/api/parcel/(\d+)/([0-9A-Za-z]+)",path)
        if not match:
            return self.answer(404,{"error":"Unknown endpoint"})
        target = ROOT / "data/registry/parcels" / match[1] / (match[2]+".json")
        if not target.exists():
            return self.answer(404,{"error":"Parcel is outside the loaded registry"})
        data = json.loads(target.read_text(encoding="utf-8"))
        with sqlite3.connect(DB) as db:
            for link in data["links"]:
                decision = db.execute("SELECT decision,note,created_at,valid_from,valid_to FROM review_events WHERE relationship_id=? ORDER BY id DESC LIMIT 1",(link["id"],)).fetchone()
                if decision:
                    link["review"] = dict(zip(["decision","note","created_at","valid_from","valid_to"],decision))
        return self.answer(200,data)

    def do_POST(self):
        if not self.trusted_host() or self.headers.get("Origin") not in ORIGINS:
            return self.answer(403,{"error":"Unapproved local origin or host"})
        if urlparse(self.path).path != "/api/review":
            return self.answer(404,{"error":"Unknown endpoint"})
        if not DB.exists():
            return self.answer(503,{"error":"Registry has not been built"})
        if self.headers.get("Content-Type","").split(";")[0] != "application/json":
            return self.answer(415,{"error":"JSON is required"})
        try:
            length = int(self.headers.get("Content-Length","0"))
            if not 0 < length <= 8192:
                raise ValueError("Invalid request size")
            data = json.loads(self.rfile.read(length))
            if not isinstance(data,dict):
                raise ValueError("Expected a review object")
            rid, decision, note = data.get("relationship_id"),data.get("decision"),data.get("note","")
            start,end=data.get('valid_from') or None,data.get('valid_to') or None
            for value in [start,end]:
                if value is not None:date.fromisoformat(value)
            if start and end and end<=start:raise ValueError('Validity end must be after start')
            if not isinstance(rid,str) or decision not in {"accepted","rejected","unreviewed"} or not isinstance(note,str) or len(note)>2000:
                raise ValueError("Invalid review fields")
            with sqlite3.connect(DB,timeout=10) as db:
                link = db.execute("SELECT kind,status FROM relationships WHERE id=?",(rid,)).fetchone()
                if not link or link[0] not in {"property_entrance","property_building","property_alias"} or link[1] != "candidate":
                    return self.answer(400,{"error":"Only existing proposed links can be reviewed"})
                stamp = datetime.now(timezone.utc).isoformat()
                db.execute("INSERT INTO review_events(relationship_id,decision,note,created_at,valid_from,valid_to) VALUES(?,?,?,?,?,?)",(rid,decision,note,stamp,start,end))
            return self.answer(200,{"relationship_id":rid,"decision":decision,"note":note,"created_at":stamp,"valid_from":start,"valid_to":end})
        except (ValueError,TypeError,json.JSONDecodeError) as exc:
            return self.answer(400,{"error":str(exc)})


if __name__ == "__main__":
    print("Property review service: http://127.0.0.1:8766 (local only)",flush=True)
    ThreadingHTTPServer(("127.0.0.1",8766),Handler).serve_forever()
