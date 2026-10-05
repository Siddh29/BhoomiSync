import {ChevronLeft,ChevronRight,Search} from 'lucide-react';
import {useEffect,useState} from 'react';
export default function ParcelSelector({parcels,selected,onSelect}) {
  const [query,setQuery]=useState(selected);
  useEffect(()=>setQuery(selected),[selected]);
  const index=parcels.findIndex(p=>p.parcel_id===selected);
  function choose(value){setQuery(value);if(parcels.some(p=>p.parcel_id===value))onSelect(value);}
  return <div className="parcel-selector"><button className="icon-button" aria-label="Previous parcel" title="Previous parcel" disabled={index<=0} onClick={()=>onSelect(parcels[index-1].parcel_id)}><ChevronLeft/></button><div className="parcel-search"><Search/><input aria-label="Find parcel" placeholder="Find parcel ID" list="parcel-options" value={query} onChange={e=>choose(e.target.value)} onBlur={()=>setQuery(selected)}/><datalist id="parcel-options">{parcels.map(p=><option key={p.parcel_id} value={p.parcel_id}>{p.status.replaceAll('_',' ')} · {p.confidence}%</option>)}</datalist></div><button className="icon-button" aria-label="Next parcel" title="Next parcel" disabled={index<0||index>=parcels.length-1} onClick={()=>onSelect(parcels[index+1].parcel_id)}><ChevronRight/></button><span className="selection-position">{index<0?'—':index+1} / {parcels.length}</span></div>;
}
