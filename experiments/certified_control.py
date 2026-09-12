"""Count-based neural rate fitting, anytime rate boxes, and robust execution.

Synthetic fully observed Markov states. Training receives event counts and
exposures only. True rates are used exclusively to simulate observations and to
evaluate held-out decision diagnostics, never to construct confidence boxes.
"""
from pathlib import Path
import json, platform
import numpy as np
import scipy
from scipy.linalg import expm
from scipy.integrate import solve_ivp
from scipy.sparse.linalg import expm_multiply
import torch
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
QMAX=4;T=2.;NSTEP=8000
BUDGETS=[2000,8000,32000];SEEDS=[5101,5102,5103]
ETA=np.geomspace(.005,1.,16);DELTA=.01
states=[(q,z) for q in range(QMAX+1) for z in range(2)];S=len(states)
qv=np.array([q for q,z in states]);zv=np.array([z for q,z in states])
active=qv>0
caps=np.broadcast_to(np.array([5.,1.5]),(S,2,2)).copy();caps[~active]=0
cost=np.broadcast_to((.03*qv*qv)[:,None],(S,2)).copy()
g=np.zeros((S,2,2));g[:,0,0]=.03;g[:,1,0]=.35;g[~active]=0
terminal=qv*(1+.2*zv)
dest=np.zeros((S,2),int)
for i,(q,z) in enumerate(states):dest[i]=[2*max(0,q-1)+z,2*q+1-z if q else i]

def true_rates():
    lam=np.zeros((S,2,2))
    for i,(q,z) in enumerate(states):
        if q:
            for a in range(2):lam[i,a]=[(.75+.10*q)*(1+.35*z)*(1+1.8*a),.35+.1*q+.12*a+.2*z]
    assert np.all(lam<=caps)
    return lam

def observations(seed):
    rng=np.random.default_rng(seed);lam=true_rates();counts=np.zeros((S,2,2),int);exposure=np.zeros((S,2));saved=[]
    for episode in range(1,max(BUDGETS)+1):
        x=2*int(rng.integers(1,QMAX+1))+int(rng.integers(2));t=0.
        while t<T and active[x]:
            a=int(rng.integers(2));rate=lam[x,a];waiting=rng.exponential(1/rate.sum());dt=min(waiting,T-t)
            exposure[x,a]+=dt;t+=dt
            if waiting>=dt+1e-14 or t>=T:break
            e=int(rng.random()>=rate[0]/rate.sum());counts[x,a,e]+=1;x=dest[x,e]
        if episode in BUDGETS:saved.append({'episodes':episode,'counts':counts.copy(),'exposure':exposure.copy()})
    return saved

def confidence(counts,exposure,delta):
    """Grid-optimized exponential counting-process confidence sequences."""
    d=int(active.sum()*2*2);logterm=np.log(2*d*len(ETA)/delta)
    lo=np.zeros_like(caps);hi=caps.copy()
    for i in np.flatnonzero(active):
        for a in range(2):
            e=exposure[i,a]
            if e==0:continue
            for mark in range(2):
                n=counts[i,a,mark]
                lo[i,a,mark]=max(0.,np.max((ETA*n-logterm)/(np.expm1(ETA)*e)))
                hi[i,a,mark]=min(caps[i,a,mark],np.min((ETA*n+logterm)/(-np.expm1(-ETA)*e)))
    assert np.all(lo<=hi),'Empty confidence intersection: report failure, do not repair silently.'
    return lo,hi

def train_rates(counts,exposure,seed):
    torch.manual_seed(seed)
    inputs=np.array([[q/QMAX,2*z-1,2*a-1] for q,z in states for a in range(2)])
    net=torch.nn.Sequential(torch.nn.Linear(3,12),torch.nn.Tanh(),torch.nn.Linear(12,2))
    x=torch.from_numpy(inputs);E=torch.from_numpy(exposure.reshape(-1,1));C=torch.from_numpy(counts.reshape(-1,2)).double()
    cap=torch.tensor([5.,1.5]);opt=torch.optim.Adam(net.parameters(),lr=.025)
    for _ in range(1400):
        lam=torch.sigmoid(net(x))*cap
        loss=((E*lam-C*torch.log(lam)).sum()/E.sum())
        opt.zero_grad();loss.backward();opt.step()
    rate=(torch.sigmoid(net(x))*cap).detach().numpy().reshape(S,2,2);rate[~active]=0
    params={k:v.detach().numpy().tolist() for k,v in net.state_dict().items()}
    return rate,{'state_dict':params,'architecture':'3-12-tanh-2-sigmoid; output caps (5,1.5)',
                 'parameters':sum(p.numel() for p in net.parameters()),'loss':float(loss.detach()),'seed':seed}

def hamilton(v,lo,hi,mode):
    gamma=g+v[dest][:,None,:]-v[:,None,None]
    rate=np.where(gamma>=0,hi,lo) if mode=='upper' else np.where(gamma>=0,lo,hi)
    action_values=cost+(rate*gamma).sum(axis=2)
    pol=np.argmin(action_values,axis=1)
    return action_values[np.arange(S),pol],pol

def euler_control(lo,hi,mode,steps=NSTEP):
    h=T/steps;envelope=float(hi.sum(axis=2).max());assert h*envelope<=1
    v=terminal.copy();resid=0.;policy=np.empty((steps,S),np.int8)
    for n in range(steps):
        rhs,p=hamilton(v,lo,hi,mode);policy[n]=p
        resid+=envelope*h*h*np.max(abs(rhs));v=v+h*rhs
    return v,float(resid),policy

def generator(rate,policy):
    mat=np.zeros((S,S));b=cost[np.arange(S),policy].copy()
    for x in range(S):
        for e in range(2):
            lam=rate[x,policy[x],e];mat[x,dest[x,e]]+=lam;mat[x,x]-=lam;b[x]+=lam*g[x,policy[x],e]
    return mat,b

def evaluate_policy(rate,policy,steps=NSTEP):
    """Exact matrix exponentiation over runs of equal time-grid feedback actions."""
    v=terminal.copy();h=T/steps;start=0;blocks=0
    while start<steps:
        stop=start+1
        while stop<steps and np.array_equal(policy[stop],policy[start]):stop+=1
        mat,b=generator(rate,policy[start]);aug=np.zeros((S+1,S+1));aug[:S,:S]=mat;aug[:S,S]=b
        v=(expm((stop-start)*h*aug)@np.r_[v,1.])[:S];start=stop;blocks+=1
    return v,blocks

def value_identity(lam,estimate,lo,hi,x0):
    policy=np.zeros(S,int);Qt,bt=generator(lam,policy);Qh,bh=generator(estimate,policy)
    aug=np.zeros((S+1,S+1));aug[:S,:S]=Qh;aug[:S,S]=bh
    vh=expm_multiply(aug,np.r_[terminal,1.],start=0,stop=T,num=2001)[:,:S]
    p0=np.eye(S)[x0];occ=expm_multiply(Qt.T,p0,start=0,stop=T,num=2001)
    gamma=g[:,0,:][None,:,:]+vh[::-1, dest]-vh[::-1,:,None]
    diff=lam[:,0,:]-estimate[:,0,:];u=np.maximum(estimate[:,0,:]-lo[:,0,:],hi[:,0,:]-estimate[:,0,:])
    signed=np.sum(occ*np.sum(diff[None,:,:]*gamma,axis=2),axis=1)
    weighted=np.max(np.sum(u[None,:,:]*abs(gamma),axis=2),axis=1)
    at=np.zeros((S+1,S+1));at[:S,:S]=Qt;at[:S,S]=bt
    vt=(expm(T*at)@np.r_[terminal,1.])[:S]
    identity=float(np.trapezoid(signed,dx=T/2000));difference=float(vt[x0]-vh[-1,x0])
    B=float(terminal.max()+T*cost.max()+QMAX*g.max())
    return {'cost_difference':difference,'signed_identity_quadrature':identity,'identity_discrepancy':abs(identity-difference),
            'continuation_confidence_bound':float(np.trapezoid(weighted,dx=T/2000)),
            'payoff_range_TV_bound':B*min(1.,T*float(u.sum(axis=1).max())),'cost_range_bound':B}

def main():
    torch.set_default_dtype(torch.float64);torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    lam=true_rates();x0=2*QMAX
    true_sol=solve_ivp(lambda t,v:hamilton(v,lam,lam,'upper')[0],[0,T],terminal,method='DOP853',rtol=2e-11,atol=2e-12)
    true_opt=true_sol.y[:,-1];true_euler,true_resid,_=euler_control(lam,lam,'upper',steps=16000)
    assert np.max(abs(true_euler-true_opt))<=true_resid
    allrows=[];full=[];saved_models=[]
    for seed in SEEDS:
        for data in observations(seed):
            n=data['episodes'];lo,hi=confidence(data['counts'],data['exposure'],DELTA/len(SEEDS))
            # This is a diagnostic against the known synthetic generator, not a proof of coverage.
            coverage=bool(np.all((lam>=lo)&(lam<=hi)));assert coverage
            raw,model=train_rates(data['counts'],data['exposure'],seed+n)
            est=np.clip(raw,lo,hi)
            up,ru,robust=euler_control(lo,hi,'upper');down,rl,_=euler_control(lo,hi,'lower')
            nominal,rn,nompol=euler_control(est,est,'upper')
            robust_actual,blocks=evaluate_policy(lam,robust);nominal_actual,_=evaluate_policy(lam,nompol)
            assert np.all(robust_actual<=up+ru+1e-9)
            assert np.all(true_opt>=down-rl-1e-9)
            row={'seed':seed,'episodes':n,'true_optimal_cost_diagnostic':float(true_opt[x0]),
                 'robust_policy_cost':float(robust_actual[x0]),'nominal_policy_cost':float(nominal_actual[x0]),
                 'robust_regret_diagnostic':float(robust_actual[x0]-true_opt[x0]),
                 'nominal_regret_diagnostic':float(nominal_actual[x0]-true_opt[x0]),
                 'regret_upper_with_time_residual':float(up[x0]-down[x0]+ru+rl),
                 'upper_value':float(up[x0]),'lower_value':float(down[x0]),
                 'upper_numerical_residual':ru,'lower_numerical_residual':rl,
                 'min_positive_exposure':float(data['exposure'][active].min()),
                 'max_interval_width':float((hi-lo).max()),'all_true_rates_inside':coverage,
                 'policy_constant_time_blocks':blocks,'rate_network_parameters':model['parameters']}
            allrows.append(row)
            full.append({**row,'counts':data['counts'].tolist(),'exposure':data['exposure'].tolist(),'rate_lower':lo.tolist(),'rate_upper':hi.tolist(),'neural_rates':raw.tolist(),'deployed_rates':est.tolist()})
            saved_models.append({'seed':seed,'episodes':n,**model,'clipped_rates':est.tolist()})
            print(seed,n,'regret',round(row['robust_regret_diagnostic'],6),'bound',round(row['regret_upper_with_time_residual'],6),flush=True)
            if seed==SEEDS[0] and n==BUDGETS[-1]:
                identity=value_identity(lam,est,lo,hi,x0);assert identity['identity_discrepancy']<2e-6
                uf,rf,pf=euler_control(lo,hi,'upper',steps=16000)
                refined={'coarse_upper':float(up[x0]),'fine_upper':float(uf[x0]),'coarse_residual':ru,'fine_residual':rf,
                         'observed_grid_difference':float(abs(up[x0]-uf[x0]))}
                assert abs(up[x0]-uf[x0])<=ru+rf
                policy_for_plot=robust.copy()
    r=.1
    report={'description':'Observed-event neural rate learning and robust finite-state execution',
            'data_scope':'Synthetic fully observed state; randomized initial inventory/regime and predictable randomized actions; no external market data',
            'confidence':1-DELTA,'joint_scope':'All 3 seeds; every state-action-mark rate; all observation times and the 3 reported prefixes',
            'horizon':T,'states':states,'actions':['passive','aggressive'],'marks':['fill','regime_change'],
            'training':{'steps':1400,'objective':'exposure-weighted Poisson negative log-likelihood','oracle_rate_labels':False},
            'eta_grid':ETA.tolist(),'time_steps':NSTEP,'rows':allrows,'observed_sufficient_statistics':full,
            'true_optimum_crosscheck':{'solver':'DOP853','Euler_steps':16000,'Euler_residual':true_resid,'max_difference':float(np.max(abs(true_opt-true_euler)))},
            'continuation_identity':identity,'time_grid_refinement':refined,
            'early_exercise_example':{'interest_rate':r,'early_reveal_value':.5*np.exp(-r),'late_reveal_value':.5*np.exp(-2*r),'European_value':.5*np.exp(-2*r)},
            'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'torch':torch.__version__},
            'arithmetic_scope':'Float64 values with analytic time-discretization residual; no claim of interval-arithmetic certification'}
    (ROOT/'results/certified_control.json').write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'models/count_trained_rates.json').write_text(json.dumps(saved_models,indent=2)+'\n')
    lines=[r'\begin{tabular}{rrrrr}',r'\toprule',r'Episodes & Neural regret & Robust regret & 99\% regret bound & Time residual \\',r'\midrule']
    for n in BUDGETS:
        rs=[r for r in allrows if r['episodes']==n]
        lines.append(f"{n:,} & {np.mean([r['nominal_regret_diagnostic'] for r in rs]):.5f} & {np.mean([r['robust_regret_diagnostic'] for r in rs]):.5f} & {max(r['regret_upper_with_time_residual'] for r in rs):.4f} & {max(r['upper_numerical_residual']+r['lower_numerical_residual'] for r in rs):.4f} "+r'\\')
    lines += [r'\bottomrule',r'\end{tabular}'];(ROOT/'tables/certified_control.tex').write_text('\n'.join(lines)+'\n')
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axs=plt.subplots(2,2,figsize=(10,7),layout='constrained')
    for seed in SEEDS:
        rs=[r for r in allrows if r['seed']==seed]
        axs[0,0].plot(BUDGETS,[r['regret_upper_with_time_residual'] for r in rs],'o-',label=f'Seed {seed-SEEDS[0]+1}')
        axs[0,1].plot(BUDGETS,[r['robust_regret_diagnostic'] for r in rs],'o-',label=f'Seed {seed-SEEDS[0]+1}')
    axs[0,0].set(xscale='log',xlabel='Observed episodes',ylabel='99% regret upper bound',title='Data-supported robust decisions');axs[0,0].legend(fontsize=8)
    axs[0,1].set(xscale='log',xlabel='Observed episodes',ylabel='Actual synthetic regret',title='Decision diagnostic, separate from bound')
    axs[1,0].bar(['Payoff-range TV','Continuation'],[identity['payoff_range_TV_bound'],identity['continuation_confidence_bound']],color=['#9d543b','#1c627d'])
    axs[1,0].set(ylabel='Fixed passive-policy error bound',title='Economic weights improve sensitivity')
    im=axs[1,1].imshow(policy_for_plot[::80,2::2].T,origin='lower',aspect='auto',extent=[0,T,.5,4.5],cmap='Blues',vmin=0,vmax=1)
    axs[1,1].set(xlabel='Remaining time',ylabel='Remaining quantity',title='Robust action, low-spread regime');axs[1,1].set_yticks([1,2,3,4]);fig.colorbar(im,ax=axs[1,1],ticks=[0,1],label='0 passive / 1 aggressive')
    fig.savefig(ROOT/'figures/certified_control.png',dpi=220,facecolor='white');plt.close(fig)
    print(json.dumps({'continuation':identity,'time_refinement':refined}),flush=True)
if __name__=='__main__':main()
