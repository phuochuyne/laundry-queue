(() => {
'use strict';
const config={"actions":[{"authentication":"required","function_id":"capability_add_and_remove_machines_e6daa139.function.get_machine","id":"capability_add_and_remove_machines_e6daa139.screen-action.load_machine_detail","method":"GET","request_schema":{"properties":{"machine_id":{"description":"ID of the machine to retrieve","format":"uuid","in":"path","type":"string"}},"required":["machine_id"],"type":"object"},"response_schema":{"properties":{"created_at":{"description":"Timestamp when machine was created","format":"date-time","type":"string"},"deleted_at":{"description":"Timestamp when machine was deleted, null if active","format":"date-time","type":"string"},"id":{"description":"Unique identifier for the machine","format":"uuid","type":"string"},"machine_number":{"description":"Machine number","type":"string"},"machine_type":{"description":"Type of machine","enum":["washer","dryer"],"type":"string"},"qr_code_payload":{"description":"QR code payload for scanning","type":"string"}},"required":["id","machine_number","machine_type","qr_code_payload","created_at"],"type":"object"},"route":"/api/capability_add_and_remove_machines_e6daa139/machines/{machine_id}","success_route":null},{"authentication":"required","function_id":"capability_add_and_remove_machines_e6daa139.function.delete_machine","id":"capability_add_and_remove_machines_e6daa139.screen-action.delete_machine_from_detail","method":"DELETE","request_schema":{"properties":{"machine_id":{"description":"ID of the machine to delete","format":"uuid","in":"path","type":"string"}},"required":["machine_id"],"type":"object"},"response_schema":{"properties":{"deleted_at":{"description":"Timestamp when machine was deleted","format":"date-time","type":"string"},"success":{"description":"Indicates successful deletion","type":"boolean"}},"required":["success"],"type":"object"},"route":"/api/capability_add_and_remove_machines_e6daa139/machines/{machine_id}","success_route":"/admin/machines"}],"screen_route":"/admin/machines/{machine_id}"};
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

// QR Code generation using QRCode.js library (assumed available in runtime)
document.addEventListener('DOMContentLoaded', function() {
  const canvas = document.getElementById('qrcode-canvas');
  const printButton = document.getElementById('print-qr-button');
  
  // Listen for data binding completion
  const observer = new MutationObserver(function(mutations) {
    const payloadTextarea = document.querySelector('[data-bind="qr_code_payload"]');
    if (payloadTextarea && payloadTextarea.value) {
      generateQRCode(payloadTextarea.value);
      observer.disconnect();
    }
  });
  
  observer.observe(document.body, {
    childList: true,
    subtree: true,
    attributes: true,
    attributeFilter: ['value']
  });
  
  function generateQRCode(payload) {
    if (typeof QRCode !== 'undefined') {
      QRCode.toCanvas(canvas, payload, {
        width: 256,
        margin: 2,
        color: {
          dark: '#0F172A',
          light: '#FFFFFF'
        }
      });
    } else {
      // Fallback: draw simple placeholder
      const ctx = canvas.getContext('2d');
      ctx.fillStyle = '#F8FAFC';
      ctx.fillRect(0, 0, 256, 256);
      ctx.fillStyle = '#0F172A';
      ctx.font = '14px Inter';
      ctx.textAlign = 'center';
      ctx.fillText('QR Code', 128, 128);
    }
  }
  
  printButton.addEventListener('click', function() {
    const machineNumber = document.querySelector('[data-bind="machine_number"]').textContent;
    const machineType = document.querySelector('[data-bind="machine_type"]').textContent;
    
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>Print QR Code - ${machineNumber}</title>
        <style>
          body {
            font-family: Inter, system-ui, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 2rem;
            margin: 0;
          }
          h1 { margin: 0 0 0.5rem 0; font-size: 2rem; }
          p { margin: 0 0 2rem 0; color: #687080; text-transform: capitalize; }
          img { border: 2px solid #E2E8F0; border-radius: 14px; padding: 1rem; }
          @media print {
            body { padding: 0; }
          }
        </style>
      </head>
      <body>
        <h1>Machine ${machineNumber}</h1>
        <p>${machineType}</p>
        <img src="${canvas.toDataURL()}" alt="QR Code" />
      </body>
      </html>
    `);
    printWindow.document.close();
    printWindow.focus();
    setTimeout(() => {
      printWindow.print();
    }, 250);
  });
});