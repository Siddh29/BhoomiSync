import {useCallback, useEffect, useRef, useState} from 'react';
import {post, request} from '../api/client';
import {LAYER_IDS} from '../api/presentation';

const empty = {summary:null, datasets:[], parcels:[], conflicts:[], changes:[], layers:{}, status:{status:'IDLE'}, demo:true};
export default function useWorkspace() {
  const [data, setData] = useState(empty);
  const [selected, setSelected] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [mutating, setMutating] = useState(false);
  const mounted = useRef(true);
  const refresh = useCallback(async () => {
    const [health, datasets, status] = await Promise.all([request('/health'), request('/datasets'), request('/harmonization/status')]);
    let results = {summary:null, parcels:[], conflicts:[], changes:[], layers:{}};
    try {
      // A reset legitimately leaves no completed snapshot. Keep source metadata available.
      const summary = await request('/results/summary');
      const [parcels, conflicts, changes, ...layers] = await Promise.all([
        request('/results/parcels'), request('/results/conflicts'), request('/results/changes'),
        ...LAYER_IDS.map(id => request(`/layers/${id}`)),
      ]);
      results = {summary, parcels, conflicts, changes, layers:Object.fromEntries(LAYER_IDS.map((id,i) => [id,layers[i]]))};
    } catch (err) {
      if (!err.message.includes('No completed run')) throw err;
    }
    if (!mounted.current) return;
    setData({demo:health.demo_mode, datasets, status, ...results});
    setSelected(current => results.parcels.some(p => p.parcel_id === current) ? current : results.parcels[0]?.parcel_id || '');
    setLoading(false);
  }, []);
  useEffect(() => {
    mounted.current = true;
    refresh().catch(err => {setError(err.message); setLoading(false);});
    return () => {mounted.current = false;};
  }, [refresh]);
  useEffect(() => {
    if (data.status.status !== 'RUNNING') return;
    let cancelled = false, timer;
    async function poll() {
      try {
        const status = await request('/harmonization/status');
        if (cancelled) return;
        setData(current => ({...current,status}));
        if (status.status === 'COMPLETED') await refresh();
        else if (status.status === 'FAILED') setError(status.error || 'Processing failed');
        else if (status.status === 'RUNNING') timer = setTimeout(poll,250);
      } catch (err) {
        if (!cancelled) {setError(err.message); setData(current => ({...current,status:{...current.status,status:'DISCONNECTED'}}));}
      }
    }
    timer = setTimeout(poll,250);
    return () => {cancelled=true; clearTimeout(timer);};
  }, [data.status.status, refresh]);
  async function run() {
    setError(''); setMutating(true);
    try {const status = await post('/harmonization/run'); setData(current => ({...current,status:{...status,progress:0,stages:[]}}));}
    catch (err) {setError(err.message);} finally {setMutating(false);}
  }
  async function reset() {
    setError(''); setMutating(true);
    try {await post('/demo/reset'); await refresh();}
    catch (err) {setError(err.message);} finally {setMutating(false);}
  }
  return {...data,selected,setSelected,error,setError,loading,refresh,run,reset,active:mutating || data.status.status === 'RUNNING'};
}
