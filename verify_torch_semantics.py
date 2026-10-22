import sys,json,math,random
from pathlib import Path
sys.path.insert(0,'dist')
from grade import execute
import torch
torch.set_num_threads(1)
root=Path(__file__).resolve().parent
by={x['id']:x for x in json.loads((root/'dist/lessons.json').read_text(encoding='utf-8'))}
funcs={}
for i,l in by.items():
 if l['runtime']=='torch':funcs[i]=execute('import torch\n'+l['solution'])[0]
count=0

def close(a,b):
 global count
 a=torch.as_tensor(a,dtype=torch.float64);b=torch.as_tensor(b,dtype=torch.float64)
 assert a.shape==b.shape,(a.shape,b.shape)
 assert torch.allclose(a,b,atol=1e-7,rtol=1e-7,equal_nan=True),(a,b)
 count+=1

def call(i,name,*a,**k):return funcs[i][name](*a,**k)
random.seed(11);torch.manual_seed(11)
for B,D in [(1,1),(1,5),(3,7),(0,4)]:
 x=torch.randn(B,D,dtype=torch.float64)
 means=[sum(row)/len(row) for row in x.tolist()]
 if B:
  close(call('t1','row_means',x),means)
  close(call('t2','center_rows',x),[[v-means[i] for v in row] for i,row in enumerate(x.tolist())])
  labels=torch.randint(D,(B,));close(call('pt02','target_scores',x,labels),[row[label] for row,label in zip(x.tolist(),labels.tolist())])
 mask=torch.rand(B,D)>.5
 wanted=[sum(v for v,m in zip(row,ms) if m)/max(1,sum(ms)) for row,ms in zip(x.tolist(),mask.tolist())]
 close(call('pt03','masked_row_mean',x,mask),wanted)
 if B:
  probs=[];logs=[]
  for row in x.tolist():
   m=max(row);z=[math.exp(v-m) for v in row];den=math.fsum(z)
   probs.append([v/den for v in z]);logs.append(m+math.log(den))
  close(call('pt06','stable_softmax',x),probs);close(call('pt07','stable_logsumexp',x),logs)
for N,M,D in [(1,1,1),(2,4,3),(3,2,5)]:
 x=torch.randn(N,D,dtype=torch.float64);y=torch.randn(M,D,dtype=torch.float64)
 close(call('pt05','pairwise_sqdist',x,y),[[sum((a-b)**2 for a,b in zip(xx,yy)) for yy in y.tolist()] for xx in x.tolist()])
for B,T,D,H in [(1,3,6,2),(2,2,8,4)]:
 x=torch.arange(B*T*D).reshape(B,T,D).double()
 expected=[[[[x[b,t,h*(D//H)+d].item() for d in range(D//H)] for t in range(T)] for h in range(H)] for b in range(B)]
 close(call('pt09','split_heads',x,H),expected)
for B,Tq,Tk,D,Dv in [(1,2,4,3,2),(2,3,3,2,4)]:
 q=torch.randn(B,Tq,D,dtype=torch.float64);k=torch.randn(B,Tk,D,dtype=torch.float64);v=torch.randn(B,Tk,Dv,dtype=torch.float64)
 def oracle(causal=False):
  out=[]
  for b in range(B):
   rows=[]
   for t in range(Tq):
    keys=list(range(min(Tk,t+1))) if causal else list(range(Tk))
    scores=[sum(q[b,t,d].item()*k[b,j,d].item() for d in range(D))/math.sqrt(D) for j in keys]
    shift=max(scores);exp=[math.exp(s-shift) for s in scores];den=sum(exp)
    rows.append([sum(e/den*v[b,j,f].item() for e,j in zip(exp,keys)) for f in range(Dv)])
   out.append(rows)
  return out
 close(call('pt10','attention',q,k,v),oracle())
 if Tq==Tk:close(call('pt29','causal_attention',q,k,v),oracle(True))
for value in [-3.4,0.,2.7]:
 close(call('t3','gradient_at',value),2*value+3)
 close(call('pt11','gradient_stages',value),[2*value+3,2*value])
 close(call('pt13','check_gradient',value,0.03),[3*value**2+4*value-4,3*value**2+4*value-4+0.03**2])
close(call('pt12','square_grad',[.5,-3.2,7.]),[1.,-6.4,14.])
for ignored in [-100,7]:
 x=torch.randn(6,4,dtype=torch.float64);y=torch.tensor([0,ignored,2,ignored,1,3]);wanted=[]
 for row,label in zip(x.tolist(),y.tolist()):
  if label==ignored:continue
  m=max(row);wanted.append(m+math.log(sum(math.exp(v-m) for v in row))-row[label])
 close(call('pt08','masked_ce',x,y,ignored),sum(wanted)/len(wanted))
x=torch.randn(2,4,3,dtype=torch.float64);mask=torch.tensor([[True,False,True,False],[False,False,False,False]])
expected=[]
for xx,mm in zip(x.tolist(),mask.tolist()):expected.append([sum(row[d] for row,m in zip(xx,mm) if m)/max(1,sum(mm)) for d in range(3)])
close(call('pt28','masked_pool',x,mask),expected)
for n in [1,7,31]:
 logits=torch.randn(n);ys=torch.randint(2,(n,));ps=(logits>=0).long().tolist();truth=ys.tolist()
 tp=sum(p==1 and y==1 for p,y in zip(ps,truth));fp=sum(p==1 and y==0 for p,y in zip(ps,truth));fn=sum(p==0 and y==1 for p,y in zip(ps,truth))
 r=call('pt22','binary_metrics',logits,ys)
 close([r['precision'],r['recall'],r['f1']],[tp/(tp+fp) if tp+fp else 0,tp/(tp+fn) if tp+fn else 0,2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0])
for C in [1,2,5]:
 yt=torch.randint(C,(17,));pred=torch.randint(C,(17,));cm=[[0]*C for _ in range(C)]
 for p,y in zip(pred.tolist(),yt.tolist()):cm[y][p]+=1
 f1=[]
 for c in range(C):
  den=sum(cm[c])+sum(row[c] for row in cm);f1.append(2*cm[c][c]/den if den else 0.)
 r=call('pt27','classification_report',pred,yt,C);close(r['confusion'],cm);close(r['macro_f1'],sum(f1)/C)
for dtype in [torch.float32,torch.float64]:
 r=call('pt26','fit_binary',torch.tensor([[-1.],[1.]],dtype=dtype),torch.tensor([0,1]),steps=1,lr=.2)
 close(r['weight'],[.1]);close(r['bias'],0.);close(r['losses'],[math.log(2)])
print('INDEPENDENT NUMERICAL / SHAPE CHECKS PASSED:',count)
