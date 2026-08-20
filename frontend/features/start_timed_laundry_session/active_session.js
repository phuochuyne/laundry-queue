(() => {
'use strict';
const config={"actions":[{"authentication":"required","function_id":"capability_start_timed_laundry_session_f115b2e6.function.get_user_active_session","id":"capability_start_timed_laundry_session_f115b2e6.screen-action.get_user_active_session","method":"GET","request_schema":{"properties":{},"type":"object"},"response_schema":{"properties":{"created_at":{"description":"Record creation timestamp","format":"date-time","type":"string"},"duration_minutes":{"description":"Total duration in minutes","type":"integer"},"id":{"description":"Session identifier","format":"uuid","type":"string"},"machine_id":{"description":"Machine being used","format":"uuid","type":"string"},"remaining_minutes":{"description":"Calculated remaining time in minutes","type":"integer"},"started_at":{"description":"When the session started","format":"date-time","type":"string"},"status":{"description":"Session status","enum":["active"],"type":"string"},"updated_at":{"description":"Record last update timestamp","format":"date-time","type":"string"},"user_id":{"description":"User who started the session","format":"uuid","type":"string"}},"type":"object"},"route":"/api/capability_start_timed_laundry_session_f115b2e6/sessions/my-active","success_route":null},{"authentication":"required","function_id":"capability_start_timed_laundry_session_f115b2e6.function.get_session","id":"capability_start_timed_laundry_session_f115b2e6.screen-action.get_session","method":"GET","request_schema":{"properties":{"session_id":{"description":"UUID of the session to retrieve (path parameter)","format":"uuid","type":"string"}},"required":["session_id"],"type":"object"},"response_schema":{"properties":{"created_at":{"description":"Record creation timestamp","format":"date-time","type":"string"},"duration_minutes":{"description":"Total duration in minutes","type":"integer"},"ended_at":{"description":"When the session ended, null if active","format":"date-time","type":["string","null"]},"id":{"description":"Session identifier","format":"uuid","type":"string"},"machine_id":{"description":"Machine being used","format":"uuid","type":"string"},"remaining_minutes":{"description":"Calculated remaining time in minutes, null if completed","type":["integer","null"]},"started_at":{"description":"When the session started","format":"date-time","type":"string"},"status":{"description":"Current session status","enum":["active","completed"],"type":"string"},"updated_at":{"description":"Record last update timestamp","format":"date-time","type":"string"},"user_id":{"description":"User who started the session","format":"uuid","type":"string"}},"type":"object"},"route":"/api/capability_start_timed_laundry_session_f115b2e6/sessions/{session_id}","success_route":null},{"authentication":"required","function_id":"capability_start_timed_laundry_session_f115b2e6.function.end_session","id":"capability_start_timed_laundry_session_f115b2e6.screen-action.end_session","method":"POST","request_schema":{"properties":{"session_id":{"description":"UUID of the session to end (path parameter)","format":"uuid","type":"string"}},"required":["session_id"],"type":"object"},"response_schema":{"properties":{"duration_minutes":{"description":"Total duration in minutes","type":"integer"},"ended_at":{"description":"When the session ended","format":"date-time","type":"string"},"id":{"description":"Session identifier","format":"uuid","type":"string"},"machine_id":{"description":"Machine that was used","format":"uuid","type":"string"},"started_at":{"description":"When the session started","format":"date-time","type":"string"},"status":{"description":"Session status","enum":["completed"],"type":"string"},"updated_at":{"description":"Record last update timestamp","format":"date-time","type":"string"},"user_id":{"description":"User who started the session","format":"uuid","type":"string"}},"type":"object"},"route":"/api/capability_start_timed_laundry_session_f115b2e6/sessions/{session_id}/end","success_route":null}],"screen_route":"/active-session"};
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

// Client-side countdown timer
(function() {
  let countdownInterval;
  let sessionId;
  
  function startCountdown(remainingMinutes, elementSelector) {
    if (countdownInterval) {
      clearInterval(countdownInterval);
    }
    
    let secondsRemaining = remainingMinutes * 60;
    const element = document.querySelector(elementSelector);
    
    function updateDisplay() {
      const minutes = Math.floor(secondsRemaining / 60);
      element.textContent = minutes;
      
      if (secondsRemaining <= 0) {
        clearInterval(countdownInterval);
        // Refresh session data when timer reaches zero
        if (sessionId) {
          const refreshSection = document.querySelector('[data-action-id="capability_start_timed_laundry_session_f115b2e6.screen-action.get_user_active_session"]');
          if (refreshSection && window.runtime) {
            window.runtime.executeAction(refreshSection);
          }
        }
      }
    }
    
    updateDisplay();
    
    countdownInterval = setInterval(() => {
      secondsRemaining -= 1;
      updateDisplay();
    }, 1000);
  }
  
  // Listen for data binding completion
  document.addEventListener('data-bound', function(event) {
    const timerElement = document.querySelector('[data-timer="countdown"]');
    const sessionIdElement = document.querySelector('input[name="session_id"]');
    
    if (timerElement && timerElement.textContent !== '--') {
      const remainingMinutes = parseInt(timerElement.textContent, 10);
      if (!isNaN(remainingMinutes) && remainingMinutes > 0) {
        startCountdown(remainingMinutes, '[data-timer="countdown"]');
      }
    }
    
    if (sessionIdElement && sessionIdElement.value) {
      sessionId = sessionIdElement.value;
    }
  });
  
  // Cleanup on page unload
  window.addEventListener('beforeunload', function() {
    if (countdownInterval) {
      clearInterval(countdownInterval);
    }
  });
})();