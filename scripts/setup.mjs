import {spawnSync} from 'node:child_process';
import {existsSync} from 'node:fs';
const win=process.platform==='win32';
const py=win?'.venv/Scripts/python.exe':'.venv/bin/python';
function run(cmd,args){const p=spawnSync(cmd,args,{stdio:'inherit'});if(p.status!==0)process.exit(p.status||1);}
if(!existsSync(py))run(win?'python':'python3',['-m','venv','.venv']);
run(py,['-m','pip','install','-r','backend/requirements.lock.txt']);
run(py,['-m','backend.demo.generate_demo_data']);
