import {Check,LoaderCircle,Minus} from 'lucide-react';
const stages=['Data Validation','CRS Harmonization','Attribute Mapping','Topology Analysis','Spatial Candidate Matching','Conflict Detection','Change Detection','Confidence Scoring','Master Layer Generation'];
export default function RunProgress({status}) {
 return <div className="pipeline-stages">{stages.map((name,i)=>{const stage=status.stages?.find(s=>s.name===name), state=stage?.status||'PENDING', Icon=state==='DONE'?Check:state==='RUNNING'?LoaderCircle:Minus;return <div className={`pipeline-stage stage-${state}`} key={name}><span className="stage-index">{String(i+1).padStart(2,'0')}</span><Icon size={15}/><strong>{name}</strong><span className="stage-state">{state==='DONE'?'Complete':state==='RUNNING'?'Running':'Pending'}</span><span className="stage-duration">{stage?.duration_ms!=null?`${stage.duration_ms} ms`:'—'}</span></div>;})}{status.error&&<p role="alert">{status.error}</p>}</div>;
}
