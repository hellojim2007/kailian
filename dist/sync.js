/* Account-isolated progress sync. Guest data is never uploaded implicitly. */
export const COURSE_ID='python-pytorch';
export const API_ORIGIN='https://python-gym-lab-1021.milky-elk-9591.chatgpt.site';
export const PAGES_URL='https://hellojim2007.github.io/kailian/';
export const MAX_PROGRESS_BYTES=8*1024*1024;
export const MAX_COMPRESSED_BYTES=1500000;
const GUEST_KEY='kaillian-v1',ACTIVE_KEY='kaillian-sync-active',TOKEN_KEY='kaillian-sync-token',FLOW_KEY='kaillian-sync-login';
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const clone=value=>JSON.parse(JSON.stringify(value));
const safeParse=value=>{try{return JSON.parse(value);}catch{return null;}};
const iso=()=>new Date().toISOString();
const validDate=value=>typeof value==='string'&&Number.isFinite(Date.parse(value));
const profile=raw=>raw&&typeof raw.id==='string'&&raw.id.length>0&&raw.id.length<=200?{id:raw.id,name:typeof raw.name==='string'?raw.name.slice(0,200):'',email:typeof raw.email==='string'?raw.email.slice(0,300):''}:null;
export const accountStorageKey=(userId,courseId=COURSE_ID)=>`kaillian-account:${encodeURIComponent(userId)}:${encodeURIComponent(courseId)}`;
export function emptyCourseProgress(){return {version:2,current:'p1',drafts:{},quiz:{},passed:{},answers:{},stats:{},inputs:{},quizRevisions:{},assessments:{version:1,drafts:{},attempts:[]}};}
export function validProgress(value){return value&&typeof value==='object'&&value.version===2&&value.drafts&&typeof value.drafts==='object'&&!Array.isArray(value.drafts)&&value.passed&&typeof value.passed==='object'&&!Array.isArray(value.passed);}
export function normalizeGuestProgress(value){if(!value||typeof value!=='object'||Array.isArray(value)||![undefined,1,2].includes(value.version))return null;const upgraded={...value,version:2};return validProgress(upgraded)?clone(upgraded):null;}
export function canLoginHere(value=globalThis.location){return Boolean(value&&value.origin===new URL(PAGES_URL).origin&&typeof value.pathname==='string'&&value.pathname.startsWith(new URL(PAGES_URL).pathname));}
export function progressByteSize(value){return new TextEncoder().encode(JSON.stringify(value)).byteLength;}
export function normalizeCloudSnapshot(raw){
 if(!raw||!Number.isSafeInteger(raw.revision)||raw.revision<0||!(raw.progress===null||validProgress(raw.progress)))throw new Error('云端进度格式不符合约定；本机内容已保留。');
 return {revision:raw.revision,progress:raw.progress===null?null:clone(raw.progress),updatedAt:validDate(raw.updatedAt)?new Date(raw.updatedAt).toISOString():null};
}
export function normalizeCache(raw,userId,courseId=COURSE_ID){
 if(!raw||raw.userId!==userId||raw.courseId!==courseId||!validProgress(raw.progress))return null;
 return {userId,courseId,progress:clone(raw.progress),revision:Number.isSafeInteger(raw.revision)&&raw.revision>=0?raw.revision:0,dirty:raw.dirty===true,writePending:raw.writePending===true,updatedAt:validDate(raw.updatedAt)?new Date(raw.updatedAt).toISOString():null,serverUpdatedAt:validDate(raw.serverUpdatedAt)?new Date(raw.serverUpdatedAt).toISOString():null};
}
/** No silent merge: dirty changes against a newer revision require a choice. */
export function planCloudReconcile(local,remote,userId,courseId=COURSE_ID){
 if(local&&(local.userId!==userId||local.courseId!==courseId))return {action:'reject',reason:'account-mismatch'};
 if(!local)return {action:'pull'};
 if(local.writePending)return {action:'conflict'};
 if(local.dirty)return local.revision===remote.revision?{action:'push'}:{action:'conflict'};
 if(local.revision!==remote.revision)return {action:'pull'};
 return {action:'noop'};
}
export function resolveConflictSnapshot(choice,local,remote,userId,courseId=COURSE_ID){
 if(!local||local.userId!==userId||local.courseId!==courseId)throw new Error('账号与本机缓存不匹配。');
 if(choice==='cloud')return {...local,progress:clone(remote.progress||emptyCourseProgress()),revision:remote.revision,dirty:false,writePending:false,serverUpdatedAt:remote.updatedAt,updatedAt:iso()};
 if(choice==='local')return {...local,revision:remote.revision,dirty:true,writePending:false,serverUpdatedAt:remote.updatedAt,updatedAt:iso()};
 throw new Error('请选择保留本机或使用云端。');
}
export function validateLoginReturn({pending,code,state,now=Date.now()}){
 return Boolean(pending&&typeof pending.verifier==='string'&&pending.verifier.length>=43&&pending.verifier.length<=128&&typeof code==='string'&&code.length>0&&code.length<=1024&&typeof state==='string'&&state===pending.state&&typeof pending.createdAt==='number'&&now>=pending.createdAt&&now-pending.createdAt<=10*60*1000);
}

export function createProgressSync({getProgress,applyProgress,toast=()=>{},onStatus=()=>{}}){
 let user=null,token=null,cache=null,phase='guest',detail='',conflict=null,modal=null,timer=null,working=false,applying=false,generation=0,runAgain=false,accountInfo=null,returnFocus=null,started=false,identityEpoch=0;
 const context=()=>({owner:user?.id,token,epoch:identityEpoch});
 const current=ctx=>Boolean(user&&user.id===ctx.owner&&token===ctx.token&&identityEpoch===ctx.epoch);
 const stateLabel=()=>({guest:'登录同步',checking:'检查云端…',saved:'已同步',dirty:'本机已保存',syncing:'正在同步…',offline:'离线 · 已保存在本机',conflict:'同步冲突待处理',expired:'登录已过期',error:'同步待重试',oversize:'进度较大 · 本机已保存'})[phase]||'进度同步';
 function status(next,message=''){phase=next;detail=message;onStatus({phase,label:stateLabel(),user:user?{...user}:null,detail});if(typeof document!=='undefined'){const button=document.getElementById('cloud-progress');if(button){const label=button.querySelector('[data-ps-label]');if(label)label.textContent=stateLabel();button.classList.toggle('has-conflict',phase==='conflict');button.title=detail;button.setAttribute('aria-label',(user?'账号 '+(user.name||user.email||'')+'，':'')+stateLabel());}}if(modal)renderModal();}
 function storageKey(){return user?accountStorageKey(user.id):GUEST_KEY;}
 function readCache(owner){try{const key=accountStorageKey(owner),meta=safeParse(localStorage.getItem(key+':meta')),progress=safeParse(localStorage.getItem(key));return normalizeCache({...meta,progress},owner);}catch{return null;}}
 function writeCache(value){
  if(!value||!user||value.userId!==user.id)throw new Error('本机缓存所属账号不匹配。');
  const key=accountStorageKey(value.userId),{progress,...meta}=value;
  localStorage.setItem(key+':meta',JSON.stringify({...meta,dirty:true,writePending:true}));
  localStorage.setItem(key,JSON.stringify(progress));localStorage.setItem(key+':meta',JSON.stringify(meta));
 }
 function backup(label,value){try{const key=accountStorageKey(user?.id||'guest')+':backup:'+Date.now()+'-'+Math.random().toString(36).slice(2,8);localStorage.setItem(key,JSON.stringify({label,at:iso(),progress:value}));return key;}catch{return null;}}
 function saveActive(){if(user)localStorage.setItem(ACTIVE_KEY,JSON.stringify(user));else localStorage.removeItem(ACTIVE_KEY);}
 function readToken(){const raw=safeParse(sessionStorage.getItem(TOKEN_KEY));return raw&&typeof raw.token==='string'&&raw.token.length<=8192&&profile(raw.user)&&validDate(raw.expiresAt)&&Date.parse(raw.expiresAt)>Date.now()?raw:null;}
 async function apply(value){if(!validProgress(value))throw new Error('进度数据无效，本机内容已保留。');applying=true;try{await applyProgress(clone(value));}finally{applying=false;}}
 function changed(){
  if(applying)return;generation++;
  try{
   const value=clone(getProgress());if(!validProgress(value))throw new Error('当前进度格式无效');
   if(!user){localStorage.setItem(GUEST_KEY,JSON.stringify(value));return;}
   if(cache&&JSON.stringify(cache.progress)===JSON.stringify(value))return;
   cache={userId:user.id,courseId:COURSE_ID,revision:cache?.revision||0,dirty:true,writePending:cache?.writePending===true,progress:value,updatedAt:iso(),serverUpdatedAt:cache?.serverUpdatedAt||null};writeCache(cache);
   if(conflict){conflict.local=clone(cache);conflict.exportedLocal=false;status('conflict','你继续写的内容已保留在本机冲突快照中。');return;}
   status(token?'dirty':'offline',token?'正在等待同步；关闭页面后可从本机缓存继续。':'账号内容已保存在这台设备，需要重新登录才能同步。');
   clearTimeout(timer);if(token)timer=setTimeout(()=>sync(),1600);
  }catch(error){status('error',`浏览器保存未完成：${error.message}。请立即导出进度，避免关闭页面后丢失。`);toast('本机保存遇到问题，请导出备份。');}
 }
 async function request(path,options={},requestToken=token){
  if(!requestToken)throw Object.assign(new Error('请先登录，再同步账号进度。'),{status:401});
  const headers={'Authorization':'Bearer '+requestToken,...options.headers};if(options.body)headers['Content-Type']='application/json';
  const response=await fetch(API_ORIGIN+path,{...options,headers,credentials:'omit',signal:AbortSignal.timeout(25000)});
  let body;try{body=await response.json();}catch{throw new Error('云端没有返回有效数据；本机进度已保留。');}
  if(!response.ok&&response.status!==409){const error=new Error(typeof body.error==='string'?body.error:body.error?.message||`云端请求未完成（${response.status}）`);error.status=response.status;throw error;}
  return {status:response.status,body};
 }
 async function sizeCheck(value){
  if(progressByteSize(value)>MAX_PROGRESS_BYTES)throw Object.assign(new Error('进度超过云端 8 MiB 限制。当前内容仍保存在本机，请导出备份；无需清空历史。'),{oversize:true});
  if(typeof CompressionStream!=='undefined'){
   const stream=new Blob([JSON.stringify(value)]).stream().pipeThrough(new CompressionStream('gzip'));
   const bytes=(await new Response(stream).arrayBuffer()).byteLength;
   if(bytes>MAX_COMPRESSED_BYTES)throw Object.assign(new Error('压缩后的进度超过云端 1.5 MB 限制。本机内容已保留，请导出备份。'),{oversize:true});
  }
 }
 function showConflict(remote){conflict={userId:user.id,local:clone(cache),remote:clone(remote),receivedAt:iso()};const localSaved=backup('同步冲突前的本机快照',cache.progress),cloudSaved=backup('同步冲突时的云端快照',remote.progress||emptyCourseProgress());status('conflict',localSaved&&cloudSaved?'云端和本机都有变化。两份快照已保留，请选择后再继续。':'云端和本机都有变化；浏览器备份空间不足，请先分别导出两份快照，再继续选择。');}
 async function sync(){
  if(!user||!token){if(user)status('offline','账号草稿在本机缓存中，重新登录后可同步。');return;}
  if(conflict){status('conflict',detail);return;}
  if(working){runAgain=true;return;}working=true;
  const ctx=context(),owner=ctx.owner,requestToken=ctx.token;
  try{
   status('syncing');
   const {body}=await request('/api/progress?course='+COURSE_ID,{},requestToken),remote=normalizeCloudSnapshot(body);
   if(!current(ctx))return;
   const plan=planCloudReconcile(cache,remote,owner);
   if(plan.action==='reject')throw new Error('缓存账号与登录账号不一致，已停止同步。');
   if(plan.action==='conflict'){showConflict(remote);return;}
   if(plan.action==='pull'){
    const next={userId:owner,courseId:COURSE_ID,revision:remote.revision,dirty:false,progress:clone(remote.progress||emptyCourseProgress()),updatedAt:iso(),serverUpdatedAt:remote.updatedAt};
    await apply(next.progress);if(!current(ctx))return;cache=next;writeCache(cache);status('saved',remote.progress?'已读取此账号的云端进度。':'这是此账号的新课程空间。访客进度仍留在本机，需要手动导入。');return;
   }
   if(plan.action==='noop'){status('saved','本机与云端版本一致。');return;}
   const pushedGeneration=generation,payload=clone(cache.progress),baseRevision=cache.revision;await sizeCheck(payload);
   if(!current(ctx))return;
   // Persist uncertainty before sending: a timeout can happen after the server
   // commits. A later GET must reconcile this, never blindly resend the PUT.
   cache.writePending=true;writeCache(cache);
   const result=await request('/api/progress?course='+COURSE_ID,{method:'PUT',body:JSON.stringify({revision:baseRevision,progress:payload})},requestToken);
   if(!current(ctx))return;
   const saved=normalizeCloudSnapshot(result.body);
   if(result.status===409){showConflict(saved);return;}
   cache={...cache,revision:saved.revision,serverUpdatedAt:saved.updatedAt,dirty:generation!==pushedGeneration,writePending:false};
   writeCache(cache);status(cache.dirty?'dirty':'saved',cache.dirty?'刚才的新编辑仍在本机，接着同步。':'云端已保存；这台设备也保留本机副本。');if(cache.dirty)runAgain=true;
  }catch(error){
   if(!current(ctx))return;
   if([400,401,403,413,415].includes(error.status)&&cache?.writePending){cache.writePending=false;try{writeCache(cache);}catch{cache.writePending=true;}}
   if(error.status===401){token=null;sessionStorage.removeItem(TOKEN_KEY);status('expired','会话已过期。本机进度完整保留，请重新登录。');}
   else status(error.oversize?'oversize':navigator.onLine===false?'offline':'error',error.message+' 本机缓存不会被云端覆盖。');
  }finally{working=false;if(runAgain){runAgain=false;if(token&&!conflict)timer=setTimeout(()=>sync(),300);}}
 }
 async function activate(owner,sessionToken){
  const previous={user,token,cache,conflict},nextUser=profile(owner);if(!nextUser)throw new Error('登录账号信息无效。');
  const epoch=++identityEpoch;clearTimeout(timer);
  user=nextUser;token=sessionToken||null;cache=readCache(user.id)||{userId:user.id,courseId:COURSE_ID,revision:0,dirty:false,progress:emptyCourseProgress(),updatedAt:iso(),serverUpdatedAt:null};
  conflict=null;
  try{saveActive();writeCache(cache);await apply(cache.progress);}
  catch(error){if(identityEpoch===epoch){({user,token,cache,conflict}=previous);try{saveActive();}catch{}}throw error;}
 }
 async function acceptReturn(){
  const hash=new URLSearchParams(location.hash.slice(1)),code=hash.get('sync_code'),state=hash.get('sync_state');if(!code&&!state)return false;
  const pending=safeParse(sessionStorage.getItem(FLOW_KEY));sessionStorage.removeItem(FLOW_KEY);
  history.replaceState(null,'',location.pathname+location.search);
  if(!validateLoginReturn({pending,code,state}))throw new Error('登录回调已过期或校验未通过。原有本机进度没有改变，请重新登录。');
  const response=await fetch(API_ORIGIN+'/api/session/exchange',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'omit',body:JSON.stringify({code,verifier:pending.verifier}),signal:AbortSignal.timeout(25000)});
  const result=await response.json();if(!response.ok||typeof result.token!=='string'||!profile(result.user)||!validDate(result.expiresAt))throw new Error(result.error?.message||'登录交换未完成，请重新登录。');
  sessionStorage.setItem(TOKEN_KEY,JSON.stringify({token:result.token,user:result.user,expiresAt:result.expiresAt}));await activate(result.user,result.token);return true;
 }
 async function start(){
  if(started)return;started=true;status('checking','正在恢复这台设备的登录与账号缓存。');
  if(!canLoginHere()){status('guest','账号登录在 GitHub Pages 在线版进行。当前进度保存在这个浏览器，请先导出 JSON，再到在线版登录并导入。');return;}
  try{
   const returned=await acceptReturn();
   if(!returned){const session=readToken(),active=profile(safeParse(localStorage.getItem(ACTIVE_KEY)));if(session)await activate(session.user,session.token);else if(active)await activate(active,null);}
   if(!user){status('guest','访客进度只保存在本机。登录后仍需手动导入，才能上传这份访客进度。');return;}
   if(!token){status('offline','已恢复此账号的本机缓存。请登录后继续同步。');return;}
   const ctx=context(),account=await request('/api/account',{},ctx.token);if(!current(ctx))return;accountInfo=account.body;
   if(!profile(accountInfo.user)||accountInfo.user.id!==user.id){token=null;sessionStorage.removeItem(TOKEN_KEY);status('expired','登录身份未确认，账号缓存仍留在本机，请重新登录。');return;}
   user=profile(accountInfo.user);saveActive();await sync();
  }catch(error){status(user?'offline':'guest',error.message);toast(error.message);}
 }
 async function beginLogin(){
  changed();if(!canLoginHere()){toast('请先导出 JSON，再打开在线版登录并导入进度。');return;}
  const bytes=crypto.getRandomValues(new Uint8Array(48)),base64=arr=>btoa(String.fromCharCode(...arr)).replaceAll('+','-').replaceAll('/','_').replaceAll('=','');
  const verifier=base64(bytes),state=base64(crypto.getRandomValues(new Uint8Array(24))),digest=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(verifier)),challenge=base64(new Uint8Array(digest));
  sessionStorage.setItem(FLOW_KEY,JSON.stringify({verifier,state,createdAt:Date.now()}));
  const target=new URL(API_ORIGIN+'/auth/connect');target.searchParams.set('returnTo',PAGES_URL);target.searchParams.set('challenge',challenge);target.searchParams.set('state',state);location.assign(target.href);
 }
 async function logout(){
  changed();clearTimeout(timer);const oldToken=token;token=null;generation++;identityEpoch++;conflict=null;
  sessionStorage.removeItem(TOKEN_KEY);user=null;cache=null;saveActive();
  const guest=normalizeGuestProgress(safeParse(localStorage.getItem(GUEST_KEY)));await apply(guest||emptyCourseProgress());status('guest','已回到原来的本机访客空间。账号缓存仍独立保留。');
  if(oldToken)try{await fetch(API_ORIGIN+'/api/session/revoke',{method:'POST',headers:{Authorization:'Bearer '+oldToken},credentials:'omit',signal:AbortSignal.timeout(15000)});}catch{toast('本机已退出；服务端注销请求未完成，会话将在到期后失效。');}
 }
 function download(value,name){const blob=new Blob([JSON.stringify(value,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
 function exportLocal(){download(user?cache?.progress||getProgress():getProgress(),`开练-${user?'账号':'访客'}-PythonPyTorch-进度.json`);}
 async function importGuest(){
  if(!user)return;const guest=normalizeGuestProgress(safeParse(localStorage.getItem(GUEST_KEY)));if(!guest){toast('没有找到可导入的本机访客进度。');return;}
  if(!backup('手动导入访客进度前的账号快照',cache.progress))throw new Error('浏览器没有足够空间保留账号旧副本。请先导出备份，再重试导入。');await apply(guest);changed();toast('已手动导入访客进度；旧账号快照也已保留，可导出。');await sync();
 }
 async function resolve(choice){
  if(!conflict||!user||conflict.userId!==user.id)return;const savedConflict=conflict;
  const localBackup=backup('同步冲突的本机副本',savedConflict.local.progress),cloudBackup=backup('同步冲突的云端副本',savedConflict.remote.progress||emptyCourseProgress());
  if(!(localBackup&&cloudBackup)&&!(savedConflict.exportedLocal&&savedConflict.exportedCloud))throw new Error('浏览器备份空间不足，请先分别导出两份快照，再点击选择；当前冲突尚未覆盖。');
  const next=resolveConflictSnapshot(choice,cache,savedConflict.remote,user.id);if(choice==='cloud')await apply(next.progress);cache=next;writeCache(cache);conflict=null;status(choice==='cloud'?'saved':'dirty',choice==='cloud'?'已明确选择使用云端；此前本机副本仍可导出。':'已明确选择上传本机；若云端又有变化仍会再次确认。');if(choice==='local')await sync();
 }
 function renderButton(){return `<button type="button" class="ps-top-button ${phase==='conflict'?'has-conflict':''}" id="cloud-progress" aria-label="${esc(user?'账号 '+(user.name||user.email||'')+'，':'')}${esc(stateLabel())}"><span class="ps-dot"></span><span data-ps-label>${esc(stateLabel())}</span></button>`;}
 function close(){modal?.remove();modal=null;returnFocus?.focus?.();}
 function open(){if(modal){modal.focus();return;}returnFocus=document.activeElement;modal=document.createElement('section');modal.className='ps-overlay';modal.setAttribute('role','dialog');modal.setAttribute('aria-modal','true');modal.setAttribute('aria-label','账号与云端进度');modal.tabIndex=-1;document.body.append(modal);renderModal();modal.focus();}
 function renderModal(){
  if(!modal)return;
  const guest=normalizeGuestProgress(safeParse(localStorage.getItem(GUEST_KEY))),guestCount=guest?Object.values(guest.passed).filter(x=>x===true).length:0;
  const loginControl=canLoginHere()?'<button class="ps-btn ps-primary" data-sync="login">登录账号，启用云同步 ↗</button>':`<a class="ps-btn ps-primary" href="${PAGES_URL}" target="_top" rel="noopener">打开在线版登录 ↗</a><p class="ps-caption">本机与源站进度请先导出 JSON，再到在线版登录账号并导入。真实 PyTorch 仍在本机运行。</p>`;
  modal.innerHTML=`<div class="ps-modal"><div class="ps-heading"><div><span>ACCOUNT / PYTHON × PYTORCH</span><h2>把进度带到另一台设备。</h2></div><button class="ps-close" data-sync="close" aria-label="关闭账号与同步">×</button></div><div class="ps-status ${phase==='conflict'?'conflict':''}"><i></i><div><b>${esc(stateLabel())}</b><p>${esc(detail||'课程、代码草稿与考核记录一起保存。')}</p></div></div>${user?`<div class="ps-user"><span class="ps-avatar">${esc((user.name||user.email||'你').slice(0,1))}</span><div><b>${esc(user.name||'已登录的学习者')}</b><small>${esc(user.email)}</small></div><button class="ps-link" data-sync="logout">退出</button></div><p class="ps-caption">当前空间：Python / PyTorch · 账号缓存独立保存。切换账号或退出后，不会把内容带到别人的空间。</p>${cache?`<div class="ps-meta"><span>云端版本 <b>${cache.revision}</b></span><span>${cache.dirty?'有本机修改待上传':'本机副本已保存'}</span></div>`:''}${conflict?`<section class="ps-conflict"><h3>先选保留哪一份</h3><p>没有自动合并，也没有覆盖。可先分别导出，再明确选择。选本机后会上传；选云端会替换当前账号的本机显示。</p><div class="ps-two"><div><b>本机草稿</b><small>${esc(cache?.updatedAt?new Date(cache.updatedAt).toLocaleString('zh-CN'):'时间未知')}</small><button class="ps-btn" data-sync="export-conflict-local">导出本机快照</button></div><div><b>云端版本 ${conflict.remote.revision}</b><small>${esc(conflict.remote.updatedAt?new Date(conflict.remote.updatedAt).toLocaleString('zh-CN'):'时间未知')}</small><button class="ps-btn" data-sync="export-conflict-cloud">导出云端快照</button></div></div><div class="ps-actions"><button class="ps-btn ps-primary" data-sync="choose-local">保留本机并上传</button><button class="ps-btn" data-sync="choose-cloud">使用云端进度</button></div></section>`:''}<div class="ps-actions">${token?`<button class="ps-btn ps-primary" data-sync="retry" ${working?'disabled':''}>现在同步</button>`:loginControl}<button class="ps-btn" data-sync="export">导出当前账号进度</button></div><details class="ps-import"><summary>手动导入这台设备的访客进度</summary><p>找到 ${guestCount} 道已通过的访客练习。只有点击下面按钮才会把这份访客进度放进当前账号，并上传云端。当前账号数据会先保留备份；访客原文件仍在。</p><button class="ps-btn" data-sync="confirm-import">选择导入访客进度</button><div id="ps-import-confirm"></div></details>`:`<p class="ps-intro">登录后，Python / PyTorch 的练习、草稿和考核可以在设备间继续。当前访客内容不会因登录自动上传。</p><div class="ps-actions">${loginControl}<button class="ps-btn" data-sync="export">先导出本机进度</button></div>`}<div class="ps-backups"><button class="ps-link" data-sync="backups">查看本机保留的备份</button><div id="ps-backup-list"></div></div><p class="ps-foot">断网时继续保存在当前设备；失败后可重试。云端单份上限 8 MiB，压缩后 1.5 MB。登录通过官方账号页面完成，本页不接收你的密码。</p></div>`;
  modal.onclick=async event=>{
   if(event.target===modal){close();return;}const button=event.target.closest('[data-sync]');if(!button)return;const action=button.dataset.sync;
   try{
    if(action==='close')close();else if(action==='login')await beginLogin();else if(action==='logout')await logout();else if(action==='retry')await sync();else if(action==='export')exportLocal();
    else if(action==='confirm-import'){modal.querySelector('#ps-import-confirm').innerHTML='<p class="ps-confirm">将使用访客这份进度替换当前账号进度并上传；账号旧副本会保留备份。</p><button class="ps-btn ps-primary" data-sync="import">确认导入并上传</button>';}
    else if(action==='import')await importGuest();else if(action==='choose-local')await resolve('local');else if(action==='choose-cloud')await resolve('cloud');
    else if(action==='export-conflict-local'&&conflict){download(conflict.local.progress,'开练-冲突本机快照.json');conflict.exportedLocal=true;}else if(action==='export-conflict-cloud'&&conflict){download(conflict.remote.progress||emptyCourseProgress(),'开练-冲突云端快照.json');conflict.exportedCloud=true;}else if(action==='backups')renderBackups();else if(action==='download-backup'){const saved=safeParse(localStorage.getItem(button.dataset.key));if(saved?.progress)download(saved.progress,'开练-本机保留快照.json');}
   }catch(error){status('error',error.message);toast(error.message);}
  };
  modal.onkeydown=event=>{if(event.key==='Escape'){event.preventDefault();close();}else if(event.key==='Tab'){const nodes=[...modal.querySelectorAll('button:not(:disabled),a[href],summary')].filter(n=>n.getClientRects().length),first=nodes[0],last=nodes.at(-1);if(event.shiftKey&&document.activeElement===first){event.preventDefault();last?.focus();}else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first?.focus();}}};
 }
 function renderBackups(){
  const prefix=accountStorageKey(user?.id||'guest')+':backup:',keys=[];for(let i=0;i<localStorage.length;i++){const key=localStorage.key(i);if(key?.startsWith(prefix))keys.push(key);}
  const target=modal?.querySelector('#ps-backup-list');if(!target)return;
  target.innerHTML=keys.length?keys.sort().reverse().map(key=>{const saved=safeParse(localStorage.getItem(key));return `<div class="ps-backup-row"><span>${esc(saved?.label||'保留快照')}<small>${esc(saved?.at?new Date(saved.at).toLocaleString('zh-CN'):'')}</small></span><button class="ps-link" data-sync="download-backup" data-key="${esc(key)}">导出</button></div>`;}).join(''):'<p>当前空间还没有额外备份。</p>';
 }
 if(typeof window!=='undefined'){
  window.addEventListener('online',()=>{if(user&&token&&!conflict)sync();});
  window.addEventListener('beforeunload',()=>{if(!applying)changed();});
 }
 return {start,changed,sync,logout,resolveConflict:resolve,renderButton,open,storageKey,isApplying:()=>applying};
}
