(() => {
'use strict';
const config={"actions":[{"authentication":"required","function_id":"capability_start_session_button_271c7167.function.get_session","id":"capability_start_session_button_271c7167.screen-action.get_session","method":"GET","request_schema":{"properties":{"session_id":{"description":"Path parameter: the session UUID to retrieve","format":"uuid","in":"path","type":"string"}},"required":[],"type":"object"},"response_schema":{"properties":{"created_at":{"description":"ISO 8601 timestamp when the record was created","format":"date-time","type":"string"},"duration_minutes":{"description":"The wash cycle duration in minutes","type":"integer"},"machine_id":{"description":"The machine being used in this session","format":"uuid","type":"string"},"session_id":{"description":"Unique identifier for the session","format":"uuid","type":"string"},"started_at":{"description":"ISO 8601 timestamp when the session was started","format":"date-time","type":"string"},"status":{"description":"Current session status","enum":["in_use","completed","cancelled"],"type":"string"},"updated_at":{"description":"ISO 8601 timestamp when the record was last updated","format":"date-time","type":"string"},"user_id":{"description":"The user who started the session","format":"uuid","type":"string"}},"required":["session_id","machine_id","user_id","started_at","duration_minutes","status"],"type":"object"},"route":"/api/capability_start_session_button_271c7167/sessions/{session_id}","success_route":null}],"screen_route":"/session/:session_id"};
const actionById=new Map(config.actions.map(action=>[action.id,action]));
const routeNames=template=>[...String(template||'').matchAll(/\{([A-Za-z_]\w*)\}/g)].map(match=>match[1]);
const previewValue=name=>name.endsWith('_id')||name==='id'?'example-id':'example';
const routeValues=()=>{
  const names=routeNames(config.screen_route);
  const pattern='^'+String(config.screen_route||'/').replace(/[.*+?^${}()|[\]\\]/g,'\\$&').replace(/\\\{([A-Za-z_]\w*)\\\}/g,'([^/]+)')+'$';
  const match=location.pathname.match(new RegExp(pattern));
  return Object.fromEntries(names.map((name,index)=>[name,match?decodeURIComponent(match[index+1]||''):previewValue(name)]));
};
const materialize=(template,values)=>String(template||'').replace(/\{([A-Za-z_]\w*)\}/g,(_,name)=>encodeURIComponent(values[name]??previewValue(name)));
const valueAt=(value,path)=>String(path||'').split('.').reduce((current,key)=>current&&typeof current==='object'?current[key]:undefined,value);
const display=value=>value==null?'—':typeof value==='object'?JSON.stringify(value):String(value);
const render=(payload,scope=document)=>scope.querySelectorAll('[data-bind]').forEach(node=>{
  const value=valueAt(payload,node.dataset.bind);
  if(value===undefined)return;
  if(Array.isArray(value)){
    const template=node.firstElementChild?.cloneNode(true);node.replaceChildren();
    value.forEach(item=>{if(template){const child=template.cloneNode(true);render(item,child);node.append(child);}else{const child=document.createElement('div');child.className='generated-item';child.textContent=display(item);node.append(child);}});
  }else node.textContent=display(value);
});
const region=(root,name)=>root.querySelector(`[data-${name}-region]`)||document.querySelector(`[data-${name}-region]`);
const show=(root,name,message)=>{const target=region(root,name);if(target){target.hidden=false;if(message)target.textContent=message;}};
const loading=(root,value)=>{root.dataset.loading=String(Boolean(value));root.querySelectorAll('button,input,textarea,select').forEach(node=>node.disabled=Boolean(value));};
const valuesFrom=root=>{const form=root.tagName==='FORM'?root:root.querySelector('form');return form?Object.fromEntries(new FormData(form).entries()):{};};
const coerce=(values,schema)=>Object.fromEntries(Object.entries(values).map(([key,value])=>{const rules=schema?.properties?.[key]||{};if(rules.type==='integer')return[key,Number.parseInt(value,10)];if(rules.type==='number')return[key,Number(value)];if(rules.type==='boolean')return[key,['true','1','on','yes'].includes(String(value).toLowerCase())];return[key,value];}));
const execute=async(root,action)=>{
  const requestSchema=action.request_schema||{};const requestValues=coerce(valuesFrom(root),requestSchema);const values={...routeValues(),...requestValues};let url=materialize(action.route,values);
  for(const name of requestSchema.required||[]){if(requestValues[name]===''||requestValues[name]===undefined){show(root,'error',`${name.replaceAll('_',' ')} is required.`);return;}}
  const pathNames=new Set(routeNames(action.route));const allowed=new Set(Object.keys(requestSchema.properties||{}));const body=Object.fromEntries(Object.entries(requestValues).filter(([key,value])=>allowed.has(key)&&!pathNames.has(key)&&value!==''));
  const headers={Accept:'application/json'};const token=localStorage.getItem('zorentia_access_token');if(action.authentication==='required'&&!token&&!window.__ZORENTIA_PREVIEW__){show(root,'error','Please sign in before using this action.');return;}if(token)headers.Authorization=`Bearer ${token}`;
  const options={method:action.method,headers};
  if(['GET','HEAD'].includes(action.method)){const query=new URLSearchParams(Object.entries(body));if(query.size)url+=`${url.includes('?')?'&':'?'}${query}`;}
  else{headers['Content-Type']='application/json';options.body=JSON.stringify(body);}
  loading(root,true);const errorRegion=region(root,'error');if(errorRegion)errorRegion.hidden=true;
  try{const response=await fetch(url,options);const payload=await response.json().catch(()=>({}));if(!response.ok)throw new Error(payload.message||payload.error||`Request failed (${response.status})`);if(payload.token)localStorage.setItem('zorentia_access_token',payload.token);render(payload,root);show(root,'success');if(action.success_route&&!window.__ZORENTIA_PREVIEW__)location.href=materialize(action.success_route,{...values,...payload});}
  catch(error){show(root,'error',error?.message||'Something went wrong. Please try again.');}
  finally{loading(root,false);}
};
document.querySelectorAll('[data-action-id]').forEach(root=>{
  const action=actionById.get(root.dataset.actionId);if(!action)return;
  if(root.tagName==='FORM')root.addEventListener('submit',event=>{event.preventDefault();execute(root,action);});
  else root.addEventListener('click',event=>{if(event.target.closest('button,[data-trigger]'))execute(root,action);});
  if(['GET','HEAD'].includes(action.method)&&root.dataset.autoload==='true')execute(root,action);
});
})();

(function() {
  let countdownInterval = null;
  let sessionData = null;

  function formatTime(minutes, seconds) {
    return String(minutes).padStart(2, '0') + ':' + String(seconds).padStart(2, '0');
  }

  function formatDateTime(isoString) {
    if (!isoString) return '--';
    const date = new Date(isoString);
    return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
  }

  function updateCountdown() {
    if (!sessionData || !sessionData.started_at || !sessionData.duration_minutes) return;

    const startTime = new Date(sessionData.started_at).getTime();
    const durationMs = sessionData.duration_minutes * 60 * 1000;
    const endTime = startTime + durationMs;
    const now = Date.now();
    const remainingMs = Math.max(0, endTime - now);

    const totalSeconds = Math.floor(remainingMs / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;

    const display = document.getElementById('countdown-display');
    if (display) {
      display.textContent = formatTime(minutes, seconds);
    }

    const progressRing = document.getElementById('progress-ring');
    if (progressRing) {
      const totalDurationMs = sessionData.duration_minutes * 60 * 1000;
      const elapsedMs = now - startTime;
      const progress = Math.min(1, Math.max(0, elapsedMs / totalDurationMs));
      const circumference = 754;
      const offset = circumference * (1 - progress);
      progressRing.style.strokeDashoffset = offset;
    }

    if (remainingMs <= 0 && countdownInterval) {
      clearInterval(countdownInterval);
    }
  }

  document.addEventListener('action:success', function(event) {
    if (event.detail.actionId === 'capability_start_session_button_271c7167.screen-action.get_session') {
      sessionData = event.detail.data;
      
      const startedTimeEl = document.getElementById('started-time');
      if (startedTimeEl && sessionData.started_at) {
        startedTimeEl.textContent = formatDateTime(sessionData.started_at);
      }

      if (countdownInterval) {
        clearInterval(countdownInterval);
      }

      updateCountdown();
      countdownInterval = setInterval(updateCountdown, 1000);
    }
  });

  document.addEventListener('beforeunload', function() {
    if (countdownInterval) {
      clearInterval(countdownInterval);
    }
  });
})();