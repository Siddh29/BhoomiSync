import {forwardRef,useEffect,useImperativeHandle,useRef,useState} from 'react';
import * as maplibre from 'maplibre-gl';
import workerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url';
import 'maplibre-gl/dist/maplibre-gl.css';
import darkStyle from './dark-style.json';
import lightStyle from './light-style.json';
maplibre.setWorkerUrl(workerUrl);
const EMPTY={type:'FeatureCollection',features:[]};
export const CLUSTER_COLORS=['#f2bc74','#7de0cd','#75a9ea','#9885cb'];
export const cityColor=mode=>mode==='clusters'?['match',['get','cluster'],0,CLUSTER_COLORS[0],1,CLUSTER_COLORS[1],2,CLUSTER_COLORS[2],CLUSTER_COLORS[3]]:mode==='hotspots'?['match',['get','significance'],'hotspot','#f29872','coldspot','#6da5ef','#527479']:['interpolate',['linear'],['get','deviation'],-.7,'#35587c',-.2,'#43878e',.2,'#85d5b1',1,'#e8cf89',2,'#f2a078'];
export const baseSources={
 dark:{type:'raster',tiles:['https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png'],tileSize:256,attribution:'© OpenStreetMap contributors © CARTO',maxzoom:20},
 light:{type:'raster',tiles:['https://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png'],tileSize:256,attribution:'© OpenStreetMap contributors © CARTO',maxzoom:20},
 satellite:{type:'raster',tiles:['https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'],tileSize:256,attribution:'Imagery © Esri, Maxar, Earthstar Geographics',maxzoom:19}
};
export function mapStyle(){return {version:8,sprite:darkStyle.sprite,glyphs:darkStyle.glyphs,sources:{...darkStyle.sources,...lightStyle.sources,satellite:baseSources.satellite},layers:[{id:'background',type:'background',paint:{'background-color':'#0c1b28'}},...[['dark',darkStyle],['light',lightStyle]].flatMap(([name,style])=>style.layers.map(layer=>({...layer,id:`base-${name}-${layer.id}`,layout:{...layer.layout,visibility:name==='dark'?'visible':'none'},...(layer.type==='background'&&name==='dark'?{paint:{'background-color':'#0c1b28'}}:{})}))),{id:'base-satellite',source:'satellite',type:'raster',layout:{visibility:'none'}}]};}
export function setBasemap(map,name){for(const layer of map.getStyle().layers)if(layer.id.startsWith('base-'))map.setLayoutProperty(layer.id,'visibility',layer.id===`base-${name}`||layer.id.startsWith(`base-${name}-`)?'visible':'none');}
export function circleFeature(lon,lat,radius){return {type:'FeatureCollection',features:[{type:'Feature',properties:{},geometry:{type:'Polygon',coordinates:[Array.from({length:65},(_,i)=>{const a=i/64*Math.PI*2;return [lon+Math.cos(a)*radius/(111320*Math.cos(lat*Math.PI/180)),lat+Math.sin(a)*radius/110540];})]}}]};}
const GeoCanvas=forwardRef(function GeoCanvas({wards,survey,mode='value',threeD=true,basemap='dark',selected,onSelect,onPoint,overlay='ortho',canopies=false,raster,fence,point,hero=false},ref){
 const host=useRef(),map=useRef(),latest=useRef();latest.current={onSelect,onPoint};
 const [ready,setReady]=useState(false),[network,setNetwork]=useState(false),[fatal,setFatal]=useState('');
 useImperativeHandle(ref,()=>({fly(lon,lat,zoom=13){map.current?.flyTo({center:[lon,lat],zoom,duration:1300,essential:false});},fit(bounds){map.current?.fitBounds([[bounds[0],bounds[1]],[bounds[2],bounds[3]]],{padding:65,duration:900,maxZoom:19});},reset(){map.current?.flyTo({center:survey?.center||[77.59,12.98],zoom:survey?17.3:10.55,pitch:survey?0:55,bearing:survey?0:-24,duration:1200});}}),[survey]);
 useEffect(()=>{
  let m,observer;
  setReady(false);
  try{
   m=new maplibre.Map({container:host.current,style:mapStyle(),center:survey?.center||[77.59,12.98],zoom:survey?17.3:hero?10.55:10.6,pitch:survey?0:threeD?55:0,bearing:survey?0:-24,canvasContextAttributes:{antialias:true},attributionControl:{compact:true},maxPitch:75});map.current=m;
   m.addControl(new maplibre.NavigationControl({visualizePitch:true}),'bottom-right');
   m.addControl(new maplibre.ScaleControl({unit:'metric'}),'bottom-left');
   m.on('error',()=>setNetwork(true));
   m.once('style.load',()=>{
    m.setLight({anchor:'viewport',color:'#d9f7ed',intensity:.45,position:[1.5,100,55]});
    m.addSource('wards',{type:'geojson',data:wards||EMPTY});
    m.addLayer({id:'ward-fill',type:'fill-extrusion',source:'wards',paint:{'fill-extrusion-color':cityColor(mode),'fill-extrusion-height':threeD?['get','extrusion_m']:0,'fill-extrusion-opacity':.88,'fill-extrusion-base':0,'fill-extrusion-vertical-gradient':true}});
    m.addLayer({id:'ward-line',type:'line',source:'wards',paint:{'line-color':'#b5e5db','line-width':.5,'line-opacity':.4}});
    m.addSource('selection',{type:'geojson',data:EMPTY});m.addLayer({id:'selection-line',source:'selection',type:'line',paint:{'line-color':'#fff3b7','line-width':3}});
    if(survey){
     for(const id of ['ortho','zones','vegetation']){m.addSource(id,{type:'image',url:`/survey/${id==='ortho'?'mosaic':id}.png`,coordinates:survey.image_coordinates});m.addLayer({id:`survey-${id}`,type:'raster',source:id,paint:{'raster-opacity':id==='ortho'?1:0,'raster-fade-duration':0}});}
     m.addSource('boundary',{type:'geojson',data:survey.boundary});m.addLayer({id:'boundary',source:'boundary',type:'line',paint:{'line-color':'#e5f89b','line-width':2.5,'line-dasharray':[3,2]}});
     m.addSource('canopies',{type:'geojson',data:survey.canopies});m.addLayer({id:'canopies',source:'canopies',type:'circle',layout:{visibility:'none'},paint:{'circle-radius':7,'circle-color':['case',['get','small_crown'],'#f6b778','#a9f2b0'],'circle-opacity':.6,'circle-stroke-color':'#edffe5','circle-stroke-width':1.5}});
    }
    m.addSource('fence',{type:'geojson',data:EMPTY});m.addLayer({id:'fence-fill',source:'fence',type:'fill',paint:{'fill-color':'#6cd6c0','fill-opacity':.2}});m.addLayer({id:'fence-line',source:'fence',type:'line',paint:{'line-color':'#96edc8','line-width':2,'line-dasharray':[3,2]}});
    m.addSource('point',{type:'geojson',data:EMPTY});m.addLayer({id:'point',source:'point',type:'circle',paint:{'circle-radius':8,'circle-color':'#f4b976','circle-stroke-color':'#fff','circle-stroke-width':3}});
    m.on('click',e=>{latest.current.onPoint?.(e.lngLat);const fs=m.queryRenderedFeatures(e.point,{layers:['ward-fill']});if(fs.length)latest.current.onSelect?.(fs[0].properties);});
    m.on('mousemove',e=>{m.getCanvas().style.cursor=latest.current.onPoint?'crosshair':m.queryRenderedFeatures(e.point,{layers:['ward-fill']}).length?'pointer':'';});
    setReady(true);
   });
   observer=new ResizeObserver(()=>m.resize());observer.observe(host.current);
  }catch(e){setFatal(e.message);}
  return()=>{observer?.disconnect();m?.remove();map.current=null;};
 },[]);
 useEffect(()=>{const m=map.current;if(!ready||!m?.getLayer('ward-fill'))return;m.getSource('wards')?.setData(wards||EMPTY);m.setPaintProperty('ward-fill','fill-extrusion-color',cityColor(mode));m.setPaintProperty('ward-fill','fill-extrusion-height',threeD?['get','extrusion_m']:0);m.easeTo({pitch:threeD?55:0,duration:650});m.setFilter('ward-fill',null);m.getSource('selection')?.setData({type:'FeatureCollection',features:wards?.features.filter(f=>f.properties.ward_id===selected)||[]});},[ready,wards,mode,threeD,selected]);
 useEffect(()=>{if(ready&&map.current?.getLayer('ward-fill'))setBasemap(map.current,basemap);},[ready,basemap]);
 useEffect(()=>{if(!ready||!survey||!map.current?.getLayer('canopies'))return;for(const id of ['zones','vegetation'])map.current.setPaintProperty(`survey-${id}`,'raster-opacity',overlay===id?.83:0);map.current.setLayoutProperty('canopies','visibility',canopies?'visible':'none');},[ready,survey,overlay,canopies]);
 useEffect(()=>{const m=map.current;if(!ready||!m?.getLayer('fence-fill'))return;if(m.getLayer('uploaded')){m.removeLayer('uploaded');m.removeSource('uploaded');}if(raster){m.addSource('uploaded',{type:'image',url:raster.image_url,coordinates:raster.image_coordinates});m.addLayer({id:'uploaded',type:'raster',source:'uploaded',paint:{'raster-opacity':.8}},'fence-fill');m.fitBounds([raster.image_coordinates[3],raster.image_coordinates[1]],{padding:50});}},[ready,raster]);
 useEffect(()=>{if(!ready||!map.current?.getSource('fence'))return;map.current.getSource('fence')?.setData(fence||EMPTY);map.current.getSource('point')?.setData(point?{type:'FeatureCollection',features:[{type:'Feature',properties:{},geometry:{type:'Point',coordinates:point}}]}:EMPTY);},[ready,fence,point]);
 return <div className="geo-canvas" ref={host}>{fatal&&<div className="geo-error">Map unavailable: {fatal}</div>}{network&&<div className="map-network-note">Basemap connection limited · local geometry remains available</div>}</div>;
});
export default GeoCanvas;
