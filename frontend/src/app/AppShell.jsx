import {useState} from 'react';
import {AlertCircle, RefreshCw, X} from 'lucide-react';
import Sidebar from './Sidebar';
import WorkspaceBar from './WorkspaceBar';
export default function AppShell({page,onNavigate,workspace,children,role,onRole,onDemo}) {
  const [collapsed,setCollapsed] = useState(false);
  const onRun=()=>{workspace.run(); onNavigate('Harmonize');};
  const onReset=()=>{workspace.reset(); onNavigate('Harmonize');};
  return <div className={`app-shell ${collapsed?'nav-collapsed':''}`}><Sidebar {...{page,collapsed,setCollapsed,role,onRole,onDemo}} onNavigate={onNavigate} demo={workspace.demo}/><div className="workspace"><WorkspaceBar {...{workspace,onRun,onReset,role}}/>{workspace.error&&<div className="error-strip" role="alert"><AlertCircle/><span>{workspace.error}</span><button className="button quiet" onClick={()=>workspace.refresh().then(()=>workspace.setError('')).catch(e=>workspace.setError(e.message))}><RefreshCw/>Retry</button><button className="icon-button" aria-label="Dismiss error" onClick={()=>workspace.setError('')}><X/></button></div>}<main className={`workspace-content ${['Map Review','City Atlas','Survey Lab'].includes(page)?'map-page':['Mission Control','Environment','Case Desk','Field Ops'].includes(page)?'studio-page':'document-page'}`}>{children}</main></div></div>;
}
