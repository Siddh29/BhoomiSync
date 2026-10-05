import {spawn} from 'node:child_process';
import {existsSync} from 'node:fs';
const py=process.platform==='win32'?'.venv/Scripts/python.exe':'.venv/bin/python';
if(!existsSync(py)){console.error('Run npm run setup first.');process.exit(1);}
const args=process.argv[2]==='test'?['-m','pytest','backend/tests','-q']:['-m','uvicorn','backend.main:app','--host','127.0.0.1','--port',process.env.BHOOMISYNC_PORT||'8001'];
const child=spawn(py,args,{stdio:'inherit'});
child.on('exit',code=>process.exit(code||0));
for(const signal of ['SIGINT','SIGTERM'])process.on(signal,()=>child.kill(signal));
