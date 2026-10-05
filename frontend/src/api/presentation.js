export const LAYER_IDS = ['cadastral', 'municipal', 'harmonized', 'gnss', 'buildings_old', 'buildings_latest', 'conflicts', 'changes'];
export const formatNumber = (value, digits = 0) => value == null ? '—' : Number(value).toLocaleString('en-IN', {minimumFractionDigits: digits, maximumFractionDigits: digits});
export const percent = (value, digits = 1) => value == null ? '—' : `${formatNumber(value, digits)}%`;
export const metres = value => value == null ? 'No observation' : `${formatNumber(value, 2)} m`;
export const titleCase = value => (value || 'Unknown').toLowerCase().replaceAll('_', ' ').replace(/\b\w/g, c => c.toUpperCase());
export const sourceName = id => ({cadastral:'Cadastral base',municipal:'Municipal GIS',revenue:'Revenue records',gnss:'GNSS survey',buildings_old:'Previous buildings',buildings_latest:'Latest buildings',harmonized:'Harmonized parcels',conflicts:'Conflict parcels',changes:'Detected changes',buildings:'Building epochs'}[id] || titleCase(id));
export const statusLabel = value => ({MATCHED:'Matched',REVIEW_REQUIRED:'Review required',CONFLICT:'Conflict',RUNNING:'Running',COMPLETED:'Complete',FAILED:'Failed',IDLE:'Not run',READY:'Ready',WARNING:'Warning',CRITICAL:'Critical',INFO:'Info',MISSING:'Missing',REJECTED:'Rejected',DISCONNECTED:'Disconnected'}[value] || titleCase(value));
export const metricEvidence = metrics => Object.entries(metrics || {}).filter(([,value])=>value!=null).map(([key,value]) => `${titleCase(key)}: ${typeof value === 'number' ? formatNumber(value, 2) : typeof value === 'object' ? JSON.stringify(value) : value}`).join(' · ');
