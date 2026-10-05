import {Layers, X} from 'lucide-react';
import {LAYER_GROUPS} from './layers';
import {formatNumber} from '../../api/presentation';
export default function LayerManager({layers,visibility,onToggle,onClose}) {
  return <aside className="layer-manager" aria-label="Layer manager"><div className="tool-panel-header"><h2><Layers/>Layers</h2><button className="icon-button" title="Close layers" aria-label="Close layers" onClick={onClose}><X/></button></div><div className="layer-manager-body">{LAYER_GROUPS.map(group=><section className="layer-group" key={group.name}><h3>{group.name}</h3>{group.layers.map(layer=><label className="layer-row" key={layer.id}><input type="checkbox" checked={!!visibility[layer.id]} onChange={()=>onToggle(layer.id)} aria-label={layer.name}/><span className={`layer-swatch swatch-${layer.kind}`} style={{'--swatch-color':layer.color}} aria-hidden="true"/><span className="layer-name">{layer.name}</span><span className="layer-count">{formatNumber(layers[layer.id]?.features.length || 0)}</span></label>)}</section>)}</div><div className="layer-panel-foot">Layer counts from the completed run</div></aside>;
}
