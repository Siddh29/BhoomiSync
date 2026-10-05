"""Persistent prototype records. Local personas are not production authentication."""
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'data' / 'operations'


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def connect():
    ROOT.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(ROOT / 'workspace.sqlite3')
    db.row_factory = sqlite3.Row
    db.execute('CREATE TABLE IF NOT EXISTS records (id TEXT PRIMARY KEY, kind TEXT NOT NULL, body TEXT NOT NULL, created_at TEXT NOT NULL)')
    db.execute('CREATE TABLE IF NOT EXISTS audit (id INTEGER PRIMARY KEY, at TEXT NOT NULL, actor TEXT NOT NULL, action TEXT NOT NULL, target TEXT NOT NULL, detail TEXT NOT NULL)')
    return db


def listing(kind):
    with connect() as db:
        return [json.loads(r['body']) for r in db.execute('SELECT body FROM records WHERE kind=? ORDER BY created_at DESC', (kind,))]


def get(kind, record_id):
    with connect() as db:
        row = db.execute('SELECT body FROM records WHERE kind=? AND id=?', (kind, record_id)).fetchone()
        return json.loads(row['body']) if row else None


def save(kind, body, actor='officer', action='created'):
    body = {**body, 'id': body.get('id') or str(uuid.uuid4()), 'updated_at': timestamp()}
    body.setdefault('created_at', body['updated_at'])
    with connect() as db:
        db.execute('INSERT OR REPLACE INTO records VALUES (?,?,?,?)', (body['id'], kind, json.dumps(body), body['created_at']))
        db.execute('INSERT INTO audit (at,actor,action,target,detail) VALUES (?,?,?,?,?)', (timestamp(), actor, f'{kind}.{action}', body['id'], json.dumps({k:v for k,v in body.items() if k not in ('content', 'path')})))
    return body


def delete(kind, record_id, actor):
    with connect() as db:
        db.execute('DELETE FROM records WHERE kind=? AND id=?', (kind, record_id))
        db.execute('INSERT INTO audit (at,actor,action,target,detail) VALUES (?,?,?,?,?)', (timestamp(), actor, f'{kind}.deleted', record_id, '{}'))


def audit():
    with connect() as db:
        return [dict(r) for r in db.execute('SELECT * FROM audit ORDER BY id DESC LIMIT 500')]
