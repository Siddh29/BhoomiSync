import {useState} from 'react';
import {Upload} from 'lucide-react';
import {request} from '../../api/client';
import {sourceName} from '../../api/presentation';
export default function UploadForm({workspace}) {
 const [role,setRole]=useState('cadastral'),[crs,setCrs]=useState('EPSG:4326'),[file,setFile]=useState(null),[busy,setBusy]=useState(false);
 async function submit(e){e.preventDefault();setBusy(true);try{if(!file)throw new Error('Select a source file');const body=new FormData();body.append('file',file);body.append('role',role);if(role!=='revenue')body.append('crs',crs);await request('/datasets/upload',{method:'POST',body});await workspace.refresh();}catch(err){workspace.setError(err.message);}finally{setBusy(false);}}
 return <form className="upload-form" onSubmit={submit}><label>Observation role<select aria-label="Source role" value={role} onChange={e=>setRole(e.target.value)}>{['cadastral','municipal','revenue','gnss','buildings_old','buildings_latest'].map(r=><option key={r} value={r}>{sourceName(r)}</option>)}</select></label><label>Declared CRS<input aria-label="Source CRS" value={crs} onChange={e=>setCrs(e.target.value)} disabled={role==='revenue'}/></label><label>Source file<input aria-label="Source file" type="file" accept={role==='revenue'?'.csv':'.geojson'} onChange={e=>setFile(e.target.files[0])}/></label><button className="button primary" disabled={busy||workspace.active}><Upload/>Validate & ingest</button></form>;
}
