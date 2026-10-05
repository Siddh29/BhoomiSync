import {statusLabel} from '../api/presentation';
export default function StatusIndicator({status, label}) {
  return <span className={`status-indicator status-${status || 'IDLE'}`}><span className="status-dot" aria-hidden="true"/>{label || statusLabel(status)}</span>;
}
