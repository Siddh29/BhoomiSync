import logging
import threading
import uuid
from backend.config import DATA, DEMO_MODE
from backend.demo.generate_demo_data import generate
from backend.services.pipeline import run_pipeline, fingerprint, STAGES
from backend.services.export import write_exports
from backend.storage.repository import SQLiteRepository


class RunManager:
    def __init__(self, data_dir=DATA, demo_mode=DEMO_MODE):
        self.data = data_dir
        self.input = data_dir / ('demo' if demo_mode else 'raw')
        self.demo_mode = demo_mode
        self.repo = SQLiteRepository(data_dir/'bhoomisync.sqlite')
        self.lock = threading.Lock()
        self.result = None
        self.state = {'status':'IDLE','stages':[], 'error':None,'progress':0}

    def initialize(self):
        self.input.mkdir(parents=True,exist_ok=True)
        if self.demo_mode and not (self.input/'cadastral.geojson').exists(): generate(self.input)
        cached = self.repo.load()
        if cached and cached.get('fingerprint') == fingerprint(self.input):
            self.result = cached
            write_exports(cached,self.data/'exports')
            self.state = {'status':'COMPLETED','stages':cached['stages'],'run_id':cached.get('run_id'),'progress':100,'cached':True,'error':None}
        elif (self.input/'cadastral.geojson').exists(): self.execute()

    def update_stage(self,stage):
        with self.lock:
            stages = [r for r in self.state['stages'] if r['index'] != stage['index']] + [stage]
            self.state = {**self.state,'stages':stages,'current_stage':stage['name'],'progress':round(100*sum(s['status']=='DONE' for s in stages)/len(STAGES))}

    def execute(self):
        try:
            result = run_pipeline(self.input,self.update_stage)
            result['run_id'] = uuid.uuid4().hex[:12]
            self.repo.save(result)
            write_exports(result,self.data/'exports')
            with self.lock:
                self.result = result
                self.state = {'status':'COMPLETED','run_id':result['run_id'],'stages':result['stages'],'progress':100,'cached':False,'error':None}
        except Exception as exc:
            logging.getLogger('BhoomiSync').exception('Harmonization failed')
            with self.lock: self.state = {**self.state,'status':'FAILED','error':str(exc)}

    def start(self,force=True):
        with self.lock:
            if self.state['status']=='RUNNING': raise RuntimeError('A run is already active')
            if not force and self.result and self.result['fingerprint']==fingerprint(self.input): return self.state.copy()
            self.state = {'status':'RUNNING','stages':[],'progress':0,'error':None}
        threading.Thread(target=self.execute,daemon=True).start()
        return {'status':'RUNNING'}

    def reset(self):
        with self.lock:
            if self.state['status']=='RUNNING': raise RuntimeError('Cannot reset during an active run')
            if not self.demo_mode: raise ValueError('Demo reset is disabled outside demo mode')
            generate(self.input)
            self.repo.clear(); self.result=None
            # Remove only our explicit generated export files.
            for filename in ('harmonized_parcels.geojson','conflicts.csv','change_report.csv','run_summary.json'):
                (self.data/'exports'/filename).unlink(missing_ok=True)
            self.state={'status':'IDLE','stages':[],'progress':0,'error':None}
        return self.state.copy()
