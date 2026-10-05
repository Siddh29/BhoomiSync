import {useState,useEffect,lazy,Suspense} from 'react';
import AppShell from './app/AppShell';
import useWorkspace from './hooks/useWorkspace';
import MapReview from './pages/MapReview';
import Conflicts from './pages/Conflicts';
import Sources from './pages/Sources';
import Harmonization from './pages/Harmonization';
import Overview from './pages/Overview';
import Export from './pages/Export';
import Mission from './pages/Mission';
import WorkspaceBoundary from './app/WorkspaceBoundary';
import {setWorkspaceRole} from './api/client';
import DemoGuide from './app/DemoGuide';
import {Loading} from './features/intelligence/shared';
const CityAtlas=lazy(()=>import('./pages/CityAtlas'));
const SurveyLab=lazy(()=>import('./pages/SurveyLab'));
const Environment=lazy(()=>import('./pages/Environment'));
const CaseDesk=lazy(()=>import('./pages/CaseDesk'));
const FieldOps=lazy(()=>import('./pages/FieldOps'));
export default function App() {
 const workspace=useWorkspace();
 const [page,setPage]=useState('Mission Control'),[demo,setDemo]=useState(false),[role,setRole]=useState('officer');
 useEffect(()=>setWorkspaceRole(role),[role]);
 function inspect(id){workspace.setSelected(id);setPage('Map Review');}
 const pages={'Mission Control':Mission,'City Atlas':CityAtlas,'Survey Lab':SurveyLab,Environment,'Case Desk':CaseDesk,'Field Ops':FieldOps,Overview,Sources,Harmonize:Harmonization,'Map Review':MapReview,Conflicts,Exports:Export};
 const Page=pages[page];
 return <><AppShell workspace={workspace} page={page} onNavigate={setPage} role={role} onRole={setRole} onDemo={()=>setDemo(true)}><WorkspaceBoundary key={page}><Suspense fallback={<Loading/>}><Page workspace={workspace} onNavigate={setPage} onInspect={inspect} role={role} onDemo={()=>setDemo(true)}/></Suspense></WorkspaceBoundary></AppShell>{demo&&<DemoGuide onNavigate={setPage} onClose={()=>setDemo(false)}/>}</>;
}
