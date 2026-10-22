from pathlib import Path
p=Path(__file__).parent/'dist/app.js'
s=p.read_text(encoding='utf-8')
if 'const navExpanded=new Set();' in s:
    raise SystemExit('The v2 UI has already been integrated; edit dist/app.js directly.')
for name in ('render','renderNav','renderContent','bindContent','renderConsole'):
    s=s.replace(f'function {name}(',f'function {name}Base(',1)
s=s.replace("let state={current:'p1',drafts:{},quiz:{},passed:{},answers:{}};","let state={current:'p1',drafts:{},quiz:{},passed:{},answers:{},stats:{},inputs:{}};")
s=s.replace("const xp = () => lessons.reduce((n,item)=>n+(state.quiz[item.id]?15:0)+(state.passed[item.id]?35:0),0);", "const xp = () => lessons.reduce((n,item)=>n+(item.quizzes||[item.quiz]).reduce((sum,_,i)=>sum+(state.quiz[i?item.id+':'+i:item.id]?15:0),0)+(state.passed[item.id]?35:0),0);")
s=s.replace("key==='quiz'&&state.quiz[l.id]", "key==='quiz'&&quizComplete(l)")
s=s.replace("function navigate(id){state.current=id;", "function navigate(id){navExpanded.add(lessons.find(x=>x.id===id)?.chapter);state.current=id;")
s=s.replace("const request={lesson:l.id,code,action};", "const request={lesson:l.id,code,action,stdin:state.inputs?.[l.id]??l.tests[0].stdin??''}; if(action==='submit'){state.stats??={};state.stats[l.id]??={attempts:0,failures:0};state.stats[l.id].attempts++;save();}")
s=s.replace("result.elapsed=((performance.now()-started)/1000).toFixed(2);outputs[l.id]=result;", "result.elapsed=((performance.now()-started)/1000).toFixed(2);outputs[l.id]=result;if(action==='submit'&&!result.ok){state.stats[l.id].failures++;save();}")
s=s.replace("lessons=await response.json();", "lessons=await response.json();try{course=await fetch('course.json',{cache:'no-store'}).then(r=>r.json());}catch{}navExpanded.add(lessons.find(x=>x.id===state.current)?.chapter??lessons[0].chapter);")
s=s.replace("fetch('lessons.json')", "fetch('lessons.json',{cache:'no-store'})")
# Initialization must run after the new lexical state has been initialized.
start=s.index("try{const response=await fetch('lessons.json'")
initial=s[start:];s=s[:start]
extension=(Path(__file__).parent/'curriculum/ui-v2.js').read_text(encoding='utf-8')
p.write_text(s+'\n'+extension+'\n'+initial,encoding='utf-8')
