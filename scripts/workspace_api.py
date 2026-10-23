"""Bounded catalogue reads and a separate, append-only local workflow ledger."""
from contextlib import closing
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import parse_qs,unquote,urlparse
import json,re,sqlite3
ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/'output/property-workspace/catalog.sqlite'
CASES=ROOT/'output/property-workspace/cases.sqlite'
def read_db():return closing(sqlite3.connect(CATALOG.as_uri()+'?mode=ro',uri=True,timeout=10))
def case_for(rid):
    if CASES.exists():
        with closing(sqlite3.connect(CASES,timeout=10)) as db:
            row=db.execute('SELECT status,note,created_at FROM case_events WHERE record_id=? ORDER BY id DESC LIMIT 1',(rid,)).fetchone()
            if row:return dict(status=row[0],note=row[1],saved_at=row[2])
    return dict(status='unreviewed',note='',saved_at=None)
def get_workspace(url):
    parsed=urlparse(url);path=parsed.path
    if not path.startswith('/api/property-workspace'):return None
    if not CATALOG.exists():return 503,dict(error='Property workspace catalogue has not been built')
    args=parse_qs(parsed.query);get=lambda k,default='':args.get(k,[default])[0]
    with read_db() as db:
        if path=='/api/property-workspace':return 200,json.loads(db.execute("SELECT value FROM metadata WHERE key='summary'").fetchone()[0])
        if path=='/api/property-workspace/search':
            q=get('q')[:200].casefold();origin=get('source','all');parcel=get('parcel');where=[];params=[]
            if parcel:
                if not re.fullmatch(r'\d+/[0-9A-Za-z]+',parcel):return 400,dict(error='Invalid parcel')
                where.append('id IN (SELECT id FROM record_parcels WHERE parcel=?)');params.append(parcel)
            scopes={'municipal':"kind='municipal_reported_key'",'ape':"kind='ape_identity'",'shared_key':"origin='shared_key'",'section_case':"origin='section_case'"}
            if origin in scopes:where.append(scopes[origin])
            elif origin!='all':return 400,dict(error='Invalid source filter')
            for term in q.split():
                where.append("search LIKE ? ESCAPE '\\'");params.append('%'+term.replace('\\','\\\\').replace('%','\\%').replace('_','\\_')+'%')
            try:offset=max(0,min(int(get('offset','0')),100000))
            except ValueError:return 400,dict(error='Invalid offset')
            sql=' WHERE '+' AND '.join(where) if where else ''
            total=db.execute('SELECT count(*) FROM records'+sql,params).fetchone()[0]
            rows=db.execute('SELECT brief FROM records'+sql+" ORDER BY CASE origin WHEN 'section_case' THEN 0 WHEN 'municipal_only' THEN 1 WHEN 'shared_key' THEN 2 ELSE 3 END,parcel,id LIMIT 50 OFFSET ?",params+[offset]).fetchall()
            return 200,dict(total=total,offset=offset,limit=50,records=[json.loads(r[0]) for r in rows])
        if path.startswith('/api/property-workspace/record/'):
            rid=unquote(path.split('/record/',1)[1]);row=db.execute('SELECT detail FROM records WHERE id=?',(rid,)).fetchone()
            if not row:return 404,dict(error='Record outside catalogue')
            record=json.loads(row[0]);fp=get('parcel')
            if fp not in record['parcels']:fp=record['parcel']
            context=json.loads(db.execute('SELECT detail FROM parcels WHERE parcel=?',(fp,)).fetchone()[0])
            # Decisions are read from the original ledger, never copied into source records.
            review_db=ROOT/'output/registry/properties.sqlite'
            if review_db.exists():
                with closing(sqlite3.connect(review_db.as_uri()+'?mode=ro',uri=True)) as ledger:
                    for link in record['connections']:
                        event=ledger.execute('SELECT decision,valid_from,valid_to FROM review_events WHERE relationship_id=? ORDER BY id DESC LIMIT 1',(link['id'],)).fetchone()
                        if event:link['review']=dict(zip(['decision','valid_from','valid_to'],event))
            return 200,dict(record=record,context=context,workflow=case_for(rid))
    return 404,dict(error='Unknown workspace endpoint')

def save_case(data):
    rid=data.get('record_id');status=data.get('status');note=data.get('note','')
    if not isinstance(rid,str) or status not in {'unreviewed','needs_document','in_progress','sources_reviewed'} or not isinstance(note,str) or len(note)>2000:raise ValueError('Invalid workflow fields')
    with read_db() as db:
        if not db.execute('SELECT 1 FROM records WHERE id=?',(rid,)).fetchone():raise ValueError('Unknown record')
    with closing(sqlite3.connect(CASES,timeout=10)) as db:
        db.execute('CREATE TABLE IF NOT EXISTS case_events(id INTEGER PRIMARY KEY,record_id TEXT NOT NULL,status TEXT NOT NULL,note TEXT NOT NULL,created_at TEXT NOT NULL)')
        stamp=datetime.now(timezone.utc).isoformat()
        db.execute('INSERT INTO case_events(record_id,status,note,created_at) VALUES(?,?,?,?)',(rid,status,note,stamp));db.commit()
    return dict(status=status,note=note,saved_at=stamp)
