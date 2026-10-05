export const API=import.meta.env.VITE_API_BASE||'/api';
let workspaceRole='officer';
export function setWorkspaceRole(role){workspaceRole=role;}
export async function request(path,options={}){
 const response=await fetch(`${API}${path}`,{...options,headers:{'X-Workspace-Role':workspaceRole,...options.headers}});
 if(!response.ok){let detail;try{detail=(await response.json()).detail;}catch{detail=response.statusText;}throw new Error(typeof detail==='string'?detail:JSON.stringify(detail));}
 return response.json();
}
export const post=(path,body={})=>request(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
