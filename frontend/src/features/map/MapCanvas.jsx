import {forwardRef,useEffect,useImperativeHandle,useRef,useState} from 'react';
import * as maplibre from 'maplibre-gl';
import workerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url';
import 'maplibre-gl/dist/maplibre-gl.css';
import {DEFINITIONS,EMPTY} from './layers';
import {mapStyle,setBasemap} from '../intelligence/GeoCanvas';
maplibre.setWorkerUrl(workerUrl);

function boundsFor(collection) {
  const bounds=new maplibre.LngLatBounds();
  const visit=coords=>{if(typeof coords[0]==='number')bounds.extend(coords);else coords.forEach(visit);};
  collection?.features.forEach(feature=>visit(feature.geometry.coordinates));
  return bounds;
}
function coordinateGrid(bounds) {
  if(bounds.isEmpty())return EMPTY;
  const west=bounds.getWest()-.003, east=bounds.getEast()+.003, south=bounds.getSouth()-.003, north=bounds.getNorth()+.003;
  const step=Math.max(.0005,Math.pow(10,Math.floor(Math.log10(Math.max(east-west,north-south))))/2);
  const features=[];
  for(let x=Math.floor(west/step)*step;x<=east&&features.length<80;x+=step)features.push({type:'Feature',properties:{},geometry:{type:'LineString',coordinates:[[x,south],[x,north]]}});
  for(let y=Math.floor(south/step)*step;y<=north&&features.length<160;y+=step)features.push({type:'Feature',properties:{},geometry:{type:'LineString',coordinates:[[west,y],[east,y]]}});
  return {type:'FeatureCollection',features};
}

const MapCanvas=forwardRef(function MapCanvas({layers,visibility,selected,onSelect,onReady,onPosition,layersOpen,night},ref) {
  const container=useRef(null),map=useRef(null),selectionMarker=useRef(null);
  const latest=useRef({layers,selected,onSelect,onPosition,layersOpen});
  latest.current={layers,selected,onSelect,onPosition,layersOpen};
  const [ready,setReady]=useState(false),[error,setError]=useState('');
  const fit=(collection,duration=200)=>{
    const bounds=boundsFor(collection);
    if(bounds.isEmpty()||!map.current)return;
    const width=container.current.clientWidth;
    map.current.fitBounds(bounds,{padding:{left:latest.current.layersOpen&&width>650?244:60,right:52,top:60,bottom:60},duration,maxZoom:20});
  };
  useImperativeHandle(ref,()=>({action(action){
    const m=map.current;if(!m||!ready)return;
    if(action==='zoomIn')m.zoomIn({duration:150});
    if(action==='zoomOut')m.zoomOut({duration:150});
    if(action==='fit')fit(latest.current.layers.harmonized);
    if(action==='reset'){m.jumpTo({bearing:0,pitch:0});fit(latest.current.layers.harmonized);}
    if(action==='selection'){
      const feature=latest.current.layers.harmonized?.features.find(f=>f.properties.parcel_id===latest.current.selected);
      if(feature)fit({type:'FeatureCollection',features:[feature]});
    }
  }}),[ready]);
  useEffect(()=>{
    let m,observer;
    try {
      m=new maplibre.Map({container:container.current,center:[77.5915,12.9715],zoom:17,attributionControl:{compact:true},style:mapStyle()});
      map.current=m;
      m.addControl(new maplibre.ScaleControl({unit:'metric',maxWidth:100}),'bottom-left');
      const initialize=()=>{
        if(m.getSource('harmonized'))return;
        m.addSource('graticule',{type:'geojson',data:EMPTY});
        m.addLayer({id:'graticule',source:'graticule',type:'line',paint:{'line-color':'#bfc9c5','line-opacity':.45,'line-width':.6}});
        for(const layer of DEFINITIONS) {
          const {id,color}=layer;
          m.addSource(id,{type:'geojson',data:EMPTY});
          if(id==='gnss') {
            m.addLayer({id,type:'circle',source:id,paint:{'circle-radius':3.5,'circle-color':color,'circle-stroke-color':'#ffffff','circle-stroke-width':1.2}});
            continue;
          }
          const fill=id==='harmonized'?.04:id==='buildings_latest'?.15:id==='changes'?.12:0;
          const stroke=id==='harmonized'?['match',['get','status'],'REVIEW_REQUIRED','#b38337','CONFLICT','#aa554e',color]
            :id==='conflicts'?['match',['get','status'],'REVIEW_REQUIRED','#b38337',color]
            :id==='changes'?['match',['get','type'],'REMOVED_BUILDING','#aa554e',color]:color;
          m.addLayer({id,type:'fill',source:id,paint:{'fill-color':color,'fill-opacity':fill}});
          const paint={'line-color':stroke,'line-width':id==='harmonized'?1.1:1,'line-opacity':id==='buildings_old'?.65:.9};
          if(['municipal','buildings_old','conflicts'].includes(id))paint['line-dasharray']=[4,2];
          m.addLayer({id:`${id}-outline`,type:'line',source:id,paint});
        }
        m.addSource('selected',{type:'geojson',data:EMPTY});
        m.addLayer({id:'selected-fill',source:'selected',type:'fill',paint:{'fill-color':'#337d71','fill-opacity':.12}});
        m.addLayer({id:'selected-halo',source:'selected',type:'line',paint:{'line-color':'#ffffff','line-width':5}});
        m.addLayer({id:'selected-outline',source:'selected',type:'line',paint:{'line-color':'#273d42','line-width':2.5}});
        m.on('click',event=>{
          const features=m.queryRenderedFeatures(event.point,{layers:['harmonized','conflicts','changes','selected-fill']});
          const id=features.find(f=>f.properties?.parcel_id)?.properties.parcel_id;
          if(id)latest.current.onSelect(id);
        });
        const popup=new maplibre.Popup({closeButton:false,closeOnClick:false,offset:12,className:'parcel-tooltip'});
        m.on('mousemove',event=>{
          latest.current.onPosition({longitude:event.lngLat.lng,latitude:event.lngLat.lat,zoom:m.getZoom()});
          const features=m.queryRenderedFeatures(event.point,{layers:['harmonized','conflicts']});
          m.getCanvas().style.cursor=features.length?'pointer':'';
          if(features.length){const p=features[0].properties;popup.setLngLat(event.lngLat).setText(`${p.parcel_id} · ${p.confidence}%`).addTo(m);}else popup.remove();
        });
        m.on('mouseout',()=>popup.remove());
        m.on('moveend',()=>{const c=m.getCenter();latest.current.onPosition({longitude:c.lng,latitude:c.lat,zoom:m.getZoom()});});
        setReady(true);onReady(true);
      };
      m.on('error',event=>setError(event.error?.message||'Map could not load'));
      m.on('style.load',initialize);if(m.isStyleLoaded())initialize();
      observer=new ResizeObserver(()=>m.resize());observer.observe(container.current);
    } catch(err) {setError(err.message);}
    return()=>{observer?.disconnect();selectionMarker.current?.remove();m?.remove();map.current=null;};
  },[]);
  useEffect(()=>{
    if(!ready||!map.current?.getSource('selected'))return;
    for(const {id} of DEFINITIONS)map.current.getSource(id)?.setData(layers[id]||EMPTY);
    map.current.getSource('graticule')?.setData(coordinateGrid(boundsFor(layers.harmonized)));
    fit(layers.harmonized,0);
  },[layers,ready]);
  useEffect(()=>{
    if(!ready||!map.current?.getSource('selected'))return;
    for(const {id} of DEFINITIONS){map.current.setLayoutProperty(id,'visibility',visibility[id]?'visible':'none');if(map.current.getLayer(`${id}-outline`))map.current.setLayoutProperty(`${id}-outline`,'visibility',visibility[id]?'visible':'none');}
  },[visibility,ready]);
  useEffect(()=>{
    if(!ready||!map.current?.getSource('selected'))return;
    const feature=layers.harmonized?.features.find(f=>f.properties.parcel_id===selected);
    map.current.getSource('selected').setData({type:'FeatureCollection',features:feature?[feature]:[]});
    selectionMarker.current?.remove();
    if(feature){
      const label=document.createElement('div');label.className='selected-parcel-label';label.textContent=selected;
      const bounds=boundsFor({type:'FeatureCollection',features:[feature]});
      selectionMarker.current=new maplibre.Marker({element:label,anchor:'bottom',offset:[0,-14]}).setLngLat(bounds.getCenter()).addTo(map.current);
    }
  },[selected,layers,ready]);
  useEffect(()=>{
    const m=map.current;if(!ready||!m?.getSource('selected'))return;
    const colors={harmonized:'#53bfbb',cadastral:'#9eaebc',municipal:'#75adf1',gnss:'#b7a0f1',buildings_latest:'#8b9cb0',buildings_old:'#a59cb9',changes:'#ecc277',conflicts:'#ed8581'};
    m.setPaintProperty('background','background-color',night?'#14222f':'#e9eeed');
    setBasemap(m,night?'dark':'light');
    m.setPaintProperty('graticule','line-color',night?'#405467':'#bfc9c5');
    m.setPaintProperty('graticule','line-opacity',night?.28:.45);
    for(const layer of DEFINITIONS){
      const color=night?colors[layer.id]:layer.color;
      if(layer.id==='gnss'){m.setPaintProperty(layer.id,'circle-color',color);continue;}
      m.setPaintProperty(layer.id,'fill-color',color);
      const stroke=layer.id==='harmonized'?['match',['get','status'],'REVIEW_REQUIRED',night?'#e3b76b':'#b38337','CONFLICT',night?'#ed8581':'#aa554e',color]:layer.id==='conflicts'?['match',['get','status'],'REVIEW_REQUIRED',night?'#e3b76b':'#b38337',color]:layer.id==='changes'?['match',['get','type'],'REMOVED_BUILDING',night?'#ed8581':'#aa554e',color]:color;
      m.setPaintProperty(layer.id+'-outline','line-color',stroke);
    }
    m.setPaintProperty('selected-fill','fill-color',night?'#8be6d8':'#337d71');
    m.setPaintProperty('selected-halo','line-color',night?'#14222f':'#ffffff');
    m.setPaintProperty('selected-outline','line-color',night?'#c5f9e8':'#273d42');
  },[night,ready]);
  return <><div className="map-canvas" ref={container} aria-label="Parcel map"/>{!ready&&!error&&<div className="map-loading">Initializing local map…</div>}{error&&<div className="map-error" role="alert">{error}</div>}</>;
});
export default MapCanvas;
