import {lazy,Suspense,useRef,useState} from 'react';
import {Map,PanelRight,ChevronDown,Sun,Moon} from 'lucide-react';
import MapToolbar from '../features/map/MapToolbar';
import LayerManager from '../features/map/LayerManager';
import ParcelSelector from '../features/map/ParcelSelector';
import ParcelInspector from '../features/map/ParcelInspector';
import {DEFAULT_VISIBILITY} from '../features/map/layers';
import {formatNumber} from '../api/presentation';
const MapCanvas=lazy(()=>import('../features/map/MapCanvas'));
export default function MapReview({workspace}) {
  const {layers,parcels,selected,setSelected,summary,loading}=workspace;
  const canvas=useRef(null);
  const [visibility,setVisibility]=useState(DEFAULT_VISIBILITY),[layersOpen,setLayersOpen]=useState(true),[inspectorOpen,setInspectorOpen]=useState(true),[ready,setReady]=useState(false);
  const [night,setNight]=useState(true);
  const [position,setPosition]=useState({longitude:77.59,latitude:12.97,zoom:17});
  const parcel=parcels.find(p=>p.parcel_id===selected);
  const compare=!!visibility.cadastral&&!!visibility.municipal;
  const action=name=>canvas.current?.action(name);
  function toggleCompare(){setVisibility(current=>({...current,cadastral:!compare,municipal:!compare}));}
  return <div className={`map-workstation ${night?'map-night':''} ${inspectorOpen?'':'inspector-hidden'}`}><div className="map-context-toolbar"><div className="map-context-title"><Map/><h1>Map Review</h1><span className="context-divider"/><span className="context-meta">{formatNumber(parcels.length)} parcels</span></div><ParcelSelector {...{parcels,selected}} onSelect={setSelected}/><div className="context-actions"><button className="icon-button theme-toggle" aria-label={night?"Switch to daylight map":"Switch to night map"} title={night?"Daylight map":"Night map"} onClick={()=>setNight(!night)}>{night?<Sun/>:<Moon/>}</button><button className="button quiet compare-action" aria-pressed={compare} onClick={toggleCompare}>Source comparison <ChevronDown/></button><button className="icon-button" title="Toggle parcel inspector" aria-label="Toggle parcel inspector" aria-pressed={inspectorOpen} onClick={()=>setInspectorOpen(!inspectorOpen)}><PanelRight/></button></div></div><div className="map-investigation"><section className="map-viewport" aria-label="Map workspace"><Suspense fallback={<div className="map-loading">Loading map renderer…</div>}><MapCanvas ref={canvas} {...{layers,parcels,visibility,selected,layersOpen,night}} onSelect={setSelected} onReady={setReady} onPosition={setPosition}/></Suspense><MapToolbar onAction={action} {...{ready,layersOpen,compare}} hasSelection={!!parcel} onLayers={()=>setLayersOpen(!layersOpen)} onCompare={toggleCompare}/>{layersOpen&&<LayerManager {...{layers,visibility}} onToggle={id=>setVisibility(current=>({...current,[id]:!current[id]}))} onClose={()=>setLayersOpen(false)}/>}{summary&&<div className="map-snapshot"><span className="snapshot-label">MASTER LAYER</span><strong>{summary.harmonized_parcels}<small>parcels</small></strong><span className="snapshot-divider"/><strong className="snapshot-review">{summary.needs_review}<small>to inspect</small></strong></div>}<div className="map-north" title="Map oriented north">N<span/></div><div className="map-legend"><span><i className="legend-matched"/>Matched</span><span><i className="legend-review"/>Review</span><span><i className="legend-conflict"/>Conflict</span><span className="map-click-hint">Click a parcel to inspect its data</span></div>{!summary&&!loading&&<div className="map-no-results"><strong>No completed master layer</strong><span>Run harmonization to populate this workspace.</span></div>}<div className="map-statusbar"><span className="map-coordinate">{formatNumber(position.longitude,5)}° E &nbsp; {formatNumber(position.latitude,5)}° N</span><span>WGS84 display</span><span>{summary?.analysis_crs||'—'} analysis</span><span className="map-zoom">Zoom {formatNumber(position.zoom,1)}</span></div></section>{inspectorOpen&&<ParcelInspector {...{parcel}} onFocus={()=>action('selection')}/>}</div></div>;
}
