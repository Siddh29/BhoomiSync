import {Component} from 'react';
import {RefreshCw} from 'lucide-react';
export default class WorkspaceBoundary extends Component {
 state={failed:false};
 static getDerivedStateFromError(){return {failed:true};}
 componentDidCatch(error){console.error('Workspace view failed',error);}
 render(){return this.state.failed?<div className="studio-loading"><strong>This view could not finish loading.</strong><p>Your saved records remain available. Reload to retry the workspace.</p><button className="s-button" onClick={()=>window.location.reload()}><RefreshCw size={14}/>Reload workspace</button></div>:this.props.children;}
}
