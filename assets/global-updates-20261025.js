 'use strict';
(function(){
 const cases={normal:['ready_for_review','Known balance: 2. Current, complete source; no overlapping use.','C-001 · S-01 · training-fixture','Review the proposal.'],overlap:['blocked','The same resource has an overlapping reservation.','S-01 · R-001','Choose another time and recheck.'],missing:['needs_information','The session balance is unknown.','C-001 · balance missing','Read the authoritative balance.'],stale:['needs_information','The source snapshot has expired.','training-fixture · expired','Read a fresh, complete source.'],zero:['blocked','The confirmed session balance is zero.','C-001 · balance=0','Ask the owner about the applicable policy.']};
 function restore(){document.querySelectorAll('[data-aib-check]').forEach(input=>{try{input.checked=localStorage.getItem('aib-global-20261025-'+input.dataset.aibCheck)==='1';}catch{}});}
 document.addEventListener('click',async event=>{
  const copy=event.target.closest('[data-aib-copy]');
  if(copy){const target=document.getElementById(copy.dataset.aibCopy),status=copy.parentElement.querySelector('[role="status"]');try{await navigator.clipboard.writeText(target.textContent);status.textContent='Copied.';}catch{status.textContent='Select the template text to copy it.';}return;}
  if(event.target.closest('[data-aib-run]')){const c=cases[document.getElementById('aib-global-scenario').value];document.getElementById('aib-global-result').textContent='Status: '+c[0]+'\nReason: '+c[1]+'\nEvidence: '+c[2]+'\nNext: '+c[3]+'\nExecuted: false';}
 });
 document.addEventListener('change',event=>{const input=event.target;if(input.matches('[data-aib-check]'))try{localStorage.setItem('aib-global-20261025-'+input.dataset.aibCheck,input.checked?'1':'0');}catch{}});
 document.addEventListener('DOMContentLoaded',()=>{
  restore();const form=document.getElementById('aib-practice-access');if(!form)return;
  form.addEventListener('submit',async event=>{
   event.preventDefault();const status=document.getElementById('aib-practice-status'),input=document.getElementById('aib-practice-password');status.textContent='Checking…';
   try{
    const payload=JSON.parse(document.getElementById('aib-practice-payload').textContent);
    const digest=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(input.value.trim()));
    const hash=Array.from(new Uint8Array(digest),b=>b.toString(16).padStart(2,'0')).join('');input.value='';
    if(!payload.hashes.includes(hash)){status.textContent='That password does not match this volume. Use the password supplied with your purchase or contact reader support.';return;}
    const content=document.getElementById('aib-practice-content');content.innerHTML=new TextDecoder().decode(Uint8Array.from(atob(payload.html64),c=>c.charCodeAt(0)));content.hidden=false;document.getElementById('aib-practice-lock').hidden=true;restore();content.scrollIntoView({block:'start'});
   }catch{input.value='';status.textContent='Access could not be checked. Open the HTTPS page in a current browser, or contact reader support.';}
  });
 });
})();
