export const LAYER_GROUPS = [
  {name:'Master layer',layers:[{id:'harmonized',name:'Harmonized parcels',color:'#337d71',kind:'polygon'}]},
  {name:'Reference boundaries',layers:[{id:'cadastral',name:'Cadastral base',color:'#4b535c',kind:'line'},{id:'municipal',name:'Municipal GIS',color:'#527fa5',kind:'dashed'}]},
  {name:'Survey observations',layers:[{id:'gnss',name:'GNSS observations',color:'#69628e',kind:'point'}]},
  {name:'Change detection',layers:[{id:'buildings_latest',name:'Latest buildings',color:'#92939a',kind:'polygon'},{id:'buildings_old',name:'Previous buildings',color:'#9d91a0',kind:'dashed'},{id:'changes',name:'Detected changes',color:'#bd8d3d',kind:'polygon'}]},
  {name:'Diagnostics',layers:[{id:'conflicts',name:'Conflict parcels',color:'#ad514b',kind:'line'}]},
];
export const DEFINITIONS=LAYER_GROUPS.flatMap(g=>g.layers);
export const DEFAULT_VISIBILITY={harmonized:true,buildings_latest:true,conflicts:true};
export const EMPTY={type:'FeatureCollection',features:[]};
