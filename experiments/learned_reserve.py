"""A complete synthetic reserve/filter/rate-network/execution experiment.

The rate network is an emulator trained on 24 known state/action specifications.
All deployed states are enumerated, so its errors are deterministic finite-domain
checks, not claims of generalization from exchange data. Exact CTMC values are
independently compared to both averaged-rate and posterior-randomized thinning.
"""
from pathlib import Path
import json
import platform
import time
import numpy as np
from scipy.linalg import expm
from scipy.integrate import quad
import scipy
import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
STATES=[(r,h) for r in range(2) for h in range(6)]
FILLED, DEPLETED = 12,13
DEADLINES=np.arange(0,1.50001,.1)
SEED=912071
PRIOR=np.zeros(12)
for r,pr in [(0,.6),(1,.4)]:
    for h,ph in [(0,.1),(2,.5),(5,.4)]:
        PRIOR[6*r+h]=pr*ph


def true_rates():
    out=np.zeros((2,12,2))
    for a in range(2):
        for i,(r,h) in enumerate(STATES):
            out[a,i]=[(1+2*r)*(1+.08*h),(.6+.5*a)*(.8+.4*r)]
    return out


class RateNet(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.net=torch.nn.Sequential(torch.nn.Linear(3,24),torch.nn.Tanh(),
            torch.nn.Linear(24,24),torch.nn.Tanh(),torch.nn.Linear(24,2))
    def forward(self,x):
        return 10*torch.sigmoid(self.net(x))


def train_rates():
    torch.manual_seed(SEED)
    model=RateNet()
    features=np.array([[2*r-1,h/2.5-1,2*a-1] for a in range(2) for r,h in STATES],float)
    x=torch.from_numpy(features)
    y=torch.from_numpy(true_rates().reshape(-1,2))
    opt=torch.optim.Adam(model.parameters(),lr=.015)
    losses=[]
    for k in range(1200):
        loss=(model(x)-y).square().mean()
        opt.zero_grad();loss.backward();opt.step()
        if k%100==0: losses.append([k,float(loss.detach())])
    opt=torch.optim.LBFGS(model.parameters(),lr=.8,max_iter=2000,
        tolerance_grad=1e-12,tolerance_change=1e-16,line_search_fn="strong_wolfe")
    def closure():
        opt.zero_grad()
        loss=(model(x)-y).square().mean()
        loss.backward()
        return loss
    opt.step(closure)
    pred=model(x).detach().numpy().reshape(2,12,2)
    weights={k:v.detach().numpy().tolist() for k,v in model.state_dict().items()}
    return pred,{"seed":SEED,"parameters":sum(v.numel() for v in model.parameters()),
        "architecture":"3-24-24-2, tanh hidden activations, 10*sigmoid rate decoder",
        "training_examples":24,"targets":"exact synthetic conditional rates; every deployed active state/action is represented",
        "optimizer":"1200 Adam steps (lr .015), then L-BFGS (max 2000 iterations)",
        "held_out_market_data":False,"final_mse":float(np.mean((pred-true_rates())**2)),
        "training_log":losses,"state_dict":weights}


def generator(rates,a):
    Q=np.zeros((14,14))
    for i,(r,h) in enumerate(STATES):
        death,fill=rates[a,i]
        Q[i,6*r+h-1 if h else DEPLETED]=death
        Q[i,FILLED]=fill
        Q[i,i]=-death-fill
    return Q


def prehistory(rates,events,end=.5,quiet=True):
    # Before posting the trader has no fill clock. Only competing executions are observed.
    p=PRIOR.copy();t=0.
    trace=[{"time":0.,"hidden_mean":float(p@np.array([h for r,h in STATES])),"fast_probability":float(p[6:].sum())}]
    for u in [*events,end]:
        if quiet:
            p*=np.exp(-(u-t)*rates[0,:,0])
            p/=p.sum()
        if u in events:
            out=np.zeros(12)
            for i,(r,h) in enumerate(STATES):
                if h:
                    out[6*r+h-1]+=p[i]*rates[0,i,0]
            p=out/out.sum()
        t=u
        trace.append({"time":u,"hidden_mean":float(p@np.array([h for r,h in STATES])),"fast_probability":float(p[6:].sum())})
    return p,trace


def law(rates,a,t,p):
    init=np.r_[p,0.,0.]
    dist=init@expm(t*generator(rates,a))
    assert abs(dist.sum()-1)<1e-11 and np.min(dist)>-1e-12
    return np.array([dist[FILLED],dist[:12].sum(),dist[DEPLETED]])


def cvar(probs,costs,alpha=.99):
    return min(z+probs@np.maximum(costs-z,0)/(1-alpha) for z in costs)


def choose(rates,p):
    records=[]
    for a in range(2):
        costs=np.array([.04*a,.3,1.])
        for t in DEADLINES:
            probs=law(rates,a,t,p)
            records.append({"a":a,"deadline":float(t),"mean_cost":float(probs@costs),
                "cvar99":float(cvar(probs,costs)),"probabilities":probs.tolist()})
    return min(records,key=lambda r:r["mean_cost"]),records


def field_constants(rates):
    truth=true_rates()
    f=np.zeros((2,12,3));g=f.copy()
    for a in range(2):
        for i,(r,h) in enumerate(STATES):
            f[a,i,0 if h else 1]=truth[a,i,0]
            g[a,i,0 if h else 1]=rates[a,i,0]
            f[a,i,2]=truth[a,i,1];g[a,i,2]=rates[a,i,1]
    delta=float(abs(f-g).sum(axis=2).max())
    rmax=float(np.linalg.norm(f-g,axis=2).max())
    K=max(np.linalg.norm(g[a,i]-g[a,j])/np.sqrt(2) for a in range(2) for i in range(12) for j in range(i))
    return {"uniform_rate_l1_error":delta,"uniform_field_l2_error":rmax,
        "latent_field_lipschitz":float(K),"latent_metric_diameter":float(np.sqrt(2)),
        "event_space_mass":3.,"proposal_envelope":float(np.ceil(rates.sum(axis=2).max()))}


def simulate(rates,a,horizon,posterior,n,seed,method):
    rng=np.random.default_rng(seed)
    envelope=float(np.ceil(rates.sum(axis=2).max()))
    counts=np.zeros(3,int);proposal_count=0
    for _ in range(n):
        p=posterior.copy();t=0.;outcome=1
        while True:
            dt=rng.exponential(1/envelope);t+=dt
            if t>horizon: break
            p*=np.exp(-dt*rates[a].sum(axis=1));p/=p.sum()
            if method=="posterior_draw":
                s=rng.choice(12,p=p)
                r,h=STATES[s]
                marked=np.array([rates[a,s,0] if h else 0.,rates[a,s,0] if not h else 0.,rates[a,s,1]])
            else:
                marked=np.zeros(3)
                for i,(r,h) in enumerate(STATES):
                    marked[0 if h else 1]+=p[i]*rates[a,i,0]
                    marked[2]+=p[i]*rates[a,i,1]
            u=rng.random()*envelope
            mark=np.searchsorted(np.cumsum(marked),u,side="right")
            proposal_count+=1
            if mark==1: outcome=2;break
            if mark==2: outcome=0;break
            if mark==0:
                new=np.zeros(12)
                for i,(r,h) in enumerate(STATES):
                    if h:new[6*r+h-1]+=p[i]*rates[a,i,0]
                p=new/new.sum()
    
        counts[outcome]+=1
    probs=counts/n;exact=law(rates,a,horizon,posterior)
    se=np.sqrt(exact*(1-exact)/n)
    assert np.all(abs(probs-exact)<5*se+1/n),(method,probs,exact,se)
    return {"method":method,"paths":n,"seed":seed,"counts":counts.tolist(),
        "probabilities":probs.tolist(),"exact_probabilities":exact.tolist(),
        "binomial_standard_errors":se.tolist(),"max_absolute_error":float(abs(probs-exact).max()),
        "proposal_count":proposal_count}


def adapted_pricing():
    rng=np.random.default_rng(847391)
    n,N,T=200000,32,1.
    dt=T/N
    brown=np.zeros(n)
    x=np.full(n,100.)
    gaps=[.005,.01,.02]
    xhat=np.full((3,n),100.)
    for k in range(N):
        sigma=.2+.1*np.tanh(brown)
        # Volatility depends only on past common innovations; every next Z is fresh.
        z=rng.standard_normal(n)
        x*=np.exp(-.5*sigma**2*dt+sigma*np.sqrt(dt)*z)
        for j,gap in enumerate(gaps):
            shat=sigma+gap
            xhat[j]*=np.exp(-.5*shat**2*dt+shat*np.sqrt(dt)*z)
        brown+=np.sqrt(dt)*z
    rows=[]
    for j,gap in enumerate(gaps):
        call=np.maximum(xhat[j]-100,0)-np.maximum(x-100,0)
        bound=100*np.exp(.32**2/2)*(1+.32)*gap
        rows.append({"volatility_shift":gap,"exact_A":gap**2*T,
            "paired_call_difference":float(call.mean()),
            "call_difference_standard_error":float(call.std(ddof=1)/np.sqrt(n)),
            "coupling_absolute_error":float(abs(xhat[j]-x).mean()),
            "deterministic_payoff_bound":float(bound)})
        assert abs(call.mean())+5*call.std(ddof=1)/np.sqrt(n)<bound
    return {"paths":n,"steps":N,"horizon":T,"sigma_bar":.32,
        "formula":"sigma_n = 0.2 + 0.1*tanh(W_n); sigma_hat_n = sigma_n + shift",
        "seed":847391,"rows":rows}


def main():
    torch.set_default_dtype(torch.float64);torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    for d in ["results","models","tables","figures"]:(ROOT/d).mkdir(exist_ok=True)
    rates,training=train_rates()
    constants=field_constants(rates)
    print("Trained rate network",json.dumps(constants),flush=True)
    (ROOT/"models/reserve_rate_network.json").write_text(json.dumps(training,indent=2)+"\n")
    scenarios={"initial":(PRIOR,PRIOR),"quiet":(prehistory(true_rates(),[])[0],prehistory(rates,[])[0]),
        "two_refreshes":(prehistory(true_rates(),[.1,.3])[0],prehistory(rates,[.1,.3])[0])}
    results=[]
    for name,(p,phat) in scenarios.items():
        best,truth=choose(true_rates(),p)
        fitted,model=choose(rates,phat)
        actual=next(r for r in truth if r["a"]==fitted["a"] and r["deadline"]==fitted["deadline"])
        tv0=float(.5*abs(p-phat).sum())
        eps=constants["uniform_rate_l1_error"]
        path_bound=tv0+(1-tv0)*(-np.expm1(-eps*DEADLINES[-1]))
        average_joint=quad(lambda t:tv0+(1-tv0)*(-np.expm1(-eps*t)),0,DEADLINES[-1],epsabs=1e-13)[0]
        field_bound=np.sqrt(3)*(constants["uniform_field_l2_error"]*DEADLINES[-1]+2*np.sqrt(2)*constants["latent_field_lipschitz"]*average_joint)
        errors=np.array([abs(x["mean_cost"]-y["mean_cost"]) for x,y in zip(truth,model)])
        assert errors.max()<=path_bound+1e-11
        assert actual["mean_cost"]-best["mean_cost"]<=2*path_bound+1e-11
        results.append({"scenario":name,"true_posterior":p.tolist(),"learned_posterior":phat.tolist(),
            "posterior_tv":tv0,"true_optimum":best,"learned_optimum":fitted,
            "actual_cost_of_learned_policy":actual["mean_cost"],"regret":actual["mean_cost"]-best["mean_cost"],
            "maximum_policy_value_error":float(errors.max()),
            "uniform_path_bound":float(path_bound),"field_posterior_path_bound":float(min(1,field_bound)),
            "uniform_regret_bound":float(2*path_bound),"cvar99_error_bound":float(min(1,path_bound/.01)),
            "all_true_policies":truth,"all_learned_policies":model})
    p,phat=scenarios["two_refreshes"]
    simulations=[simulate(rates,1,.8,phat,20000,91300+i,method)
        for i,method in enumerate(["averaged","posterior_draw"])]
    exact_filter,trace=prehistory(true_rates(),[.1,.3])
    event_only,_=prehistory(true_rates(),[.1,.3],quiet=False)
    # Independent likelihood over initial states and the two specified refresh marks.
    brute=np.zeros(12)
    for r,h in STATES:
        if h<2:continue
        initial=PRIOR[6*r+h]
        l0,l1,l2=[(1+2*r)*(1+.08*(h-j)) for j in range(3)]
        brute[6*r+h-2]+=initial*np.exp(-.1*l0)*l0*np.exp(-.2*l1)*l1*np.exp(-.2*l2)
    brute/=brute.sum()
    assert np.max(abs(brute-exact_filter))<1e-12
    assert all(h-1>=0 for r,h in STATES if h>0)
    report={"kind":"Complete synthetic learned-rate reserve simulator; no market calibration",
        "states":[list(s) for s in STATES],"initial_prior":PRIOR.tolist(),
        "rate_training":{k:v for k,v in training.items() if k!="state_dict"},
        "true_rates":true_rates().tolist(),"learned_rates":rates.tolist(),
        "constants":constants,"policy_class_size":32,"scenarios":results,
        "filter":{"observed_refresh_times":[.1,.3],"decision_time":.5,
            "trace":trace,"exact_posterior":exact_filter.tolist(),
            "event_only_posterior":event_only.tolist(),"event_only_tv_error":float(.5*abs(event_only-exact_filter).sum()),
            "direct_likelihood_residual":float(abs(brute-exact_filter).max())},
        "simulation_checks":simulations,"adapted_pricing":adapted_pricing(),
        "environment":{"python":platform.python_version(),"numpy":np.__version__,"torch":torch.__version__,"scipy":scipy.__version__}}
    (ROOT/"results/learned_reserve.json").write_text(json.dumps(report,indent=2)+"\n")
    lines=[r"\begin{tabular}{lrrrrr}",r"\toprule",
        r"History & Action & Deadline & True cost & Max. value error & Path bound \\",r"\midrule"]
    for r in results:
        b=r["learned_optimum"]
        lines.append(f"{r['scenario'].replace('_',' ')} & {b['a']} & {b['deadline']:.1f} & {r['actual_cost_of_learned_policy']:.6f} & {r['maximum_policy_value_error']:.2e} & {r['uniform_path_bound']:.2e} "+r"\\")
    lines += [r"\bottomrule",r"\end{tabular}"]
    (ROOT/"tables/learned_reserve.tex").write_text("\n".join(lines)+"\n")
    plt.rcParams.update({"font.size":11,"axes.spines.top":False,"axes.spines.right":False})
    fig,ax=plt.subplots(1,2,figsize=(10,3.8),layout="constrained")
    for r in results:
        vals=r["all_true_policies"]
        ax[0].plot(DEADLINES,[min(v["mean_cost"] for v in vals if v["deadline"]==t) for t in DEADLINES],label=r["scenario"].replace('_',' '))
    ax[0].set(xlabel="Crossing deadline",ylabel="Expected cost per lot",title="Optimal deadline depends on history")
    ax[0].legend(fontsize=9)
    positions=np.arange(3)
    for k,r in enumerate(simulations):
        ax[1].bar(positions+(k-.5)*.23,r["probabilities"],width=.23,label=r["method"].replace('_',' '))
    ax[1].plot(positions,simulations[0]["exact_probabilities"],"ko",label="Matrix exponential")
    ax[1].set_xticks(positions,["Filled","Still active","Depleted"])
    ax[1].set(ylabel="Probability",title="Two exact thinning implementations")
    ax[1].legend(fontsize=8)
    fig.savefig(ROOT/"figures/learned_reserve.png",dpi=220,bbox_inches="tight",facecolor="white");plt.close(fig)
    print(json.dumps({"scenarios":[{k:r[k] for k in ["scenario","regret","maximum_policy_value_error","uniform_path_bound","cvar99_error_bound"]} for r in results],
        "simulation_errors":[s["max_absolute_error"] for s in simulations]}),flush=True)


if __name__=="__main__":main()
