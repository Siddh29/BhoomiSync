import {lazy,Suspense} from 'react';
import {ArrowUpRight,ArrowRight,Layers3,ScanLine,Workflow,ShieldCheck,Play,MapPin,Globe2} from 'lucide-react';
import {useResource,Kicker,Loading,num} from '../features/intelligence/shared';
const GeoCanvas=lazy(()=>import('../features/intelligence/GeoCanvas'));
export default function Mission({workspace,onNavigate,onDemo}){
 const city=useResource('/city/wards'), insights=useResource('/city/insights');
 const s=workspace.summary||{};
 return <div className="mission-page">
  <section className="mission-hero">
   <div className="mission-map"><Suspense fallback={<Loading/>}>{city.data&&<GeoCanvas wards={city.data} hero/>}</Suspense></div><div className="mission-shade"/>
   <div className="mission-copy"><Kicker>LAND INTELLIGENCE, CONNECTED</Kicker><h1>One land.<br/>Many records.<br/><em>One clear picture.</em></h1><p>From fragmented records to spatial evidence.<br/>Integrate, investigate and act with confidence.</p><div className="mission-actions"><button className="s-button accent" onClick={()=>onNavigate('City Atlas')}>Explore the living atlas<ArrowUpRight size={16}/></button><button className="s-button glass" onClick={onDemo}><Play size={14}/>4-minute walkthrough</button></div><div className="mission-trust"><span><i/> LOCAL WORKSPACE READY</span><span>SIH26013 / MINISTRY OF RURAL DEVELOPMENT</span></div></div>
   <div className="hero-map-label"><Globe2 size={16}/><div><strong>BENGALURU, INDIA</strong><small>243 ward polygons · 3D spatial index</small></div><span>12.97° N<br/>77.59° E</span></div>
   <div className="hero-map-key"><span/><span/><span/><span/><small>Proxy index · DataMeet wards · OpenFreeMap / © OpenStreetMap</small></div>
  </section>
  <div className="mission-stat-row"><div><span>01 / INTEGRATE</span><strong>6 <small>source roles</small></strong><p>Cadastral · municipal · revenue · GNSS · imagery</p></div><div><span>02 / UNDERSTAND</span><strong>{insights.data?.count||'243'} <small>mapped wards</small></strong><p>Clusters, spatial hotspots and inequality</p></div><div><span>03 / RECONCILE</span><strong>{workspace.parcels?.length||'—'} <small>master parcels</small></strong><p>{workspace.conflicts?.length||0} issues with measurable evidence · prototype dataset</p></div><div><span>04 / ACCOUNT</span><strong>SHA-256 <small>integrity</small></strong><p>Persistent reviews, documents and decision history</p></div></div>
  <section className="mission-workflows"><div className="section-lead"><div><Kicker>THE WORKSPACE</Kicker><h2>Follow the evidence.</h2></div><p>One connected workflow, from city context<br/>to an individual land record.</p></div><div className="workflow-cards">{[
   ['01',Layers3,'Urban intelligence','A city-scale view of patterns, clusters and spatial disparities.','City Atlas','243 WARDS / REAL GEOMETRY'],
   ['02',Workflow,'Record harmonization','Reproject, align and reconcile six sources into one traceable master.','Harmonize','9 STAGES / EXPLAINABLE MATCHING'],
   ['03',ScanLine,'Survey intelligence','Inspect local imagery, vegetation zones and candidate tree crowns.','Survey Lab','IMAGERY ANALYSIS / GEOTIFF SUPPORT'],
   ['04',ShieldCheck,'Evidence & action','Review a case, verify a document and dispatch a field task.','Case Desk','PERSISTENT / HUMAN-IN-THE-LOOP']
  ].map(([id,Icon,title,description,page,tag])=><button key={id} className="workflow-card" onClick={()=>onNavigate(page)}><div className="workflow-card-top"><Icon/><span>{id}</span></div><h3>{title}</h3><p>{description}</p><footer><small>{tag}</small><ArrowUpRight/></footer></button>)}</div></section>
  <footer className="mission-footer"><span><MapPin size={13}/>Bengaluru records + Kallapuram survey are separate study areas</span><button onClick={()=>onNavigate('Sources')}>Inspect data provenance<ArrowRight size={13}/></button></footer>
 </div>;
}
