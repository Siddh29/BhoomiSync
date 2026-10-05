const origin=process.env.BHOOMISYNC_API_URL||'http://127.0.0.1:8001';
const response=await fetch(`${origin}/api/demo/reset`,{method:'POST'});
if(!response.ok)throw new Error(await response.text());
console.log('Demo reset. Start harmonization in the UI.');
