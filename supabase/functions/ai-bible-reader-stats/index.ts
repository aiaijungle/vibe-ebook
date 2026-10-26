const SITE_ORIGIN = "https://aiaijungle.github.io";
const BOOKS = new Set(["book1","book2","book3","book4","book5","catalog","overview"]);
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const buckets = new Map<string,{start:number;count:number}>();
let cached: {at:number;data:unknown}|null = null;

function response(req:Request,data:unknown,status=200):Response {
 return new Response(JSON.stringify(data),{status,headers:{
  "Content-Type":"application/json; charset=utf-8",
  "Access-Control-Allow-Origin":SITE_ORIGIN,
  "Access-Control-Allow-Methods":"GET, POST, OPTIONS",
  "Access-Control-Allow-Headers":"authorization, apikey, content-type, x-client-info",
  "Access-Control-Max-Age":"600","Cache-Control":"no-store","Vary":"Origin",
  "X-Content-Type-Options":"nosniff"
 }});
}
async function hash(kind:string,id:string):Promise<string> {
 const bytes=await crypto.subtle.digest("SHA-256",new TextEncoder().encode("ai-bible:v1:"+kind+":"+id));
 return Array.from(new Uint8Array(bytes),b=>b.toString(16).padStart(2,"0")).join("");
}
function allowedRate(key:string):boolean {
 const now=Date.now(); const b=buckets.get(key);
 if (!b || now-b.start>=60000) {
  if(buckets.size>5000) for(const [k,v] of buckets) if(now-v.start>=60000)buckets.delete(k);
  buckets.set(key,{start:now,count:1}); return true;
 }
 b.count+=1; return b.count<=30;
}
Deno.serve(async(req:Request)=>{
 if(req.headers.get("origin")!==SITE_ORIGIN) return response(req,{error:"origin_not_allowed"},403);
 if(req.method==="OPTIONS")return response(req,{ok:true});
 if(!["GET","POST"].includes(req.method))return response(req,{error:"method_not_allowed"},405);
 const service=Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
 const base=Deno.env.get("SUPABASE_URL");
 if(!service||!base)return response(req,{error:"stats_unavailable"},503);
 // verify_jwt=true authenticates the project JWT at the platform gateway.
 // Do not compare forwarded API headers to runtime-injected key aliases.
 let params:Record<string,unknown>={p_action:"stats"};
 try {
  if(req.method==="GET"&&cached&&Date.now()-cached.at<3000)return response(req,cached.data);
  if(req.method==="POST"){
   const bodyText=await req.text();
   if(bodyText.length>1024)return response(req,{error:"invalid_request"},400);
   const body=JSON.parse(bodyText);
   if(!body || !["heartbeat","leave"].includes(body.action) ||
     !UUID.test(body.visitorId||"") || !UUID.test(body.tabId||"") ||
     !BOOKS.has(body.bookId) || typeof body.reading!=="boolean")
    return response(req,{error:"invalid_request"},400);
   const visitorHash=await hash("visitor",body.visitorId);
   if(!allowedRate(visitorHash))return response(req,{error:"rate_limited"},429);
   params={p_action:body.action,p_visitor_hash:visitorHash,
    p_tab_hash:await hash("tab",body.tabId),p_book_id:body.bookId,p_reading:body.reading};
  }
  const upstream=await fetch(base+"/rest/v1/rpc/ai_bible_reader_stats",{
   method:"POST",headers:{"Content-Type":"application/json",apikey:service,
    Authorization:"Bearer "+service},body:JSON.stringify(params),
   signal:AbortSignal.timeout(8000)
  });
  if(!upstream.ok){
   console.error("AI Bible stats RPC failed",upstream.status);
   return response(req,{error:"stats_unavailable"},502);
  }
  const data=await upstream.json();
  if(!data || !Number.isSafeInteger(data.total_visits) || !Number.isSafeInteger(data.active_readers))
   return response(req,{error:"stats_unavailable"},502);
  cached={at:Date.now(),data};
  return response(req,data);
 } catch {
  return response(req,{error:"stats_unavailable"},503);
 }
});

