import json
import sqlite3
from abc import ABC, abstractmethod


class Repository(ABC):
    @abstractmethod
    def load(self): ...
    @abstractmethod
    def save(self, result): ...
    @abstractmethod
    def clear(self): ...


class SQLiteRepository(Repository):
    def __init__(self,path):
        self.path = path
        path.parent.mkdir(parents=True,exist_ok=True)
        with sqlite3.connect(path) as db:
            db.execute('CREATE TABLE IF NOT EXISTS snapshot (id INTEGER PRIMARY KEY CHECK(id=1), payload TEXT NOT NULL)')

    def load(self):
        with sqlite3.connect(self.path) as db:
            row = db.execute('SELECT payload FROM snapshot WHERE id=1').fetchone()
            return json.loads(row[0]) if row else None

    def save(self,result):
        payload = json.dumps(result,allow_nan=False)
        with sqlite3.connect(self.path) as db:
            db.execute('INSERT OR REPLACE INTO snapshot VALUES (1,?)',(payload,))

    def clear(self):
        with sqlite3.connect(self.path) as db:
            db.execute('DELETE FROM snapshot')
