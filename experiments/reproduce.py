"""Reproduce the synthetic, untrained examples in the finance manuscript."""
from pathlib import Path
import json
import platform
import numpy as np
import scipy
from scipy.linalg import expm
from scipy.special import expit, zeta
from scipy.stats import poisson, norm, wasserstein_distance
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
for directory in ("figures", "tables", "results"):
    (ROOT / directory).mkdir(exist_ok=True)
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11.5,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": .18, "figure.dpi": 140,
    "savefig.dpi": 220, "legend.fontsize": 10,
})
BLUE, RED, GREEN, GREY = "#23658a", "#bd583b", "#337b66", "#596574"
checks = {}

def save(fig, name):
    fig.savefig(ROOT / "figures" / name, bbox_inches="tight", facecolor="white")
    plt.close(fig)

def filtering():
    rng = np.random.default_rng(20260911)
    horizon, slow, fast, prior = 4.0, 1.0, 4.0, .5
    events = np.cumsum(rng.exponential(1 / fast, 100))
    events = events[events <= horizon]
    t = np.linspace(0, horizon, 1601)
    count = np.searchsorted(events, t, side="right")
    logodds = np.log(prior/(1-prior)) + count*np.log(fast/slow) - (fast-slow)*t
    posterior = expit(logodds)
    q0, q1 = poisson.sf(3, slow), poisson.sf(3, fast)
    predictive = (1-posterior)*q0 + posterior*q1
    frozen = (1-prior)*q0 + prior*q1
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.5), layout="constrained")
    ax[0].plot(t, posterior, color=BLUE, lw=2)
    ax[0].axhline(prior, color=GREY, ls="--", label="Snapshot prior")
    ax[0].vlines(events, 0, .035, color=RED, lw=1)
    ax[0].set(xlabel="Observation time", ylabel="Probability of fast regime",
              ylim=(0, 1.02), title="Bayesian liquidity-regime filter")
    ax[0].legend(loc="lower right")
    ax[1].plot(t, predictive, color=GREEN, lw=2, label="Conditioned on event history")
    ax[1].axhline(frozen, color=GREY, ls="--", label="Snapshot-only prediction")
    ax[1].set(xlabel="Observation time", ylabel="Probability of ≥4 arrivals in next unit",
              ylim=(0, .62), title="A decision-relevant forecast")
    ax[1].legend(loc="lower right")
    save(fig, "hidden_liquidity_filter.png")
    # Independently evaluate the two Poisson likelihoods at the final count.
    likelihood0 = poisson.pmf(len(events), slow*horizon)
    likelihood1 = poisson.pmf(len(events), fast*horizon)
    bayes = prior*likelihood1/((1-prior)*likelihood0+prior*likelihood1)
    checks["filter_logodds_vs_bayes"] = float(abs(bayes-posterior[-1]))
    return {"seed": 20260911, "true_regime": "fast", "events": events.tolist(),
            "final_posterior": float(posterior[-1]),
            "final_predictive_probability": float(predictive[-1]),
            "snapshot_predictive_probability": float(frozen)}

def queue_generator(theta=0.0):
    Q = np.zeros((7, 7))
    for n in range(1, 7):
        Q[n, n-1] = (1+theta)*(1+.25*n)
        if n < 6:
            Q[n, n+1] = 1.2
        Q[n, n] = -Q[n].sum()
    return Q

def queue_and_resolution():
    Q, T, initial = queue_generator(), 2.0, 4
    p = expm(T*Q)[initial]
    # Block exponential computes integral_0^T exp(tQ) dt without inverting Q.
    block = np.zeros((14, 14))
    block[:7, :7] = Q
    block[:7, 7:] = np.eye(7)
    occupancy = expm(T*block)[:7, 7:][initial]
    deaths = np.array([0]+[1+.25*n for n in range(1, 7)])
    expected_death_count = float(occupancy @ deaths)
    theta_values = [.001, .002, .01, .025, .05, .10, .20]
    rows = []
    for theta in theta_values:
        phat = expm(T*queue_generator(theta))[initial]
        bound_mean = min(1.0, theta*expected_death_count)
        bound_uniform = -np.expm1(-T*theta*deaths.max())
        kl = expected_death_count*(theta-np.log1p(theta))
        kl_bound = min(1., np.sqrt(kl/2))
        rows.append({
            "theta": theta, "true_depletion": float(p[0]),
            "model_depletion": float(phat[0]),
            "depletion_error": float(abs(phat[0]-p[0])),
            "terminal_tv": float(.5*np.abs(phat-p).sum()),
            "mean_path_tv_bound": bound_mean,
            "uniform_path_tv_bound": float(bound_uniform),
            "path_kl": float(kl), "kl_path_tv_bound": float(kl_bound),
            "cvar99_bound_over_B": float(min(1., min(bound_mean,bound_uniform,kl_bound)/.01)),
        })
    checks["queue_row_sums"] = float(np.max(np.abs(Q.sum(axis=1))))
    checks["occupancy_total_time"] = float(abs(occupancy.sum()-T))
    checks["queue_bounds_pass"] = all(
        r["depletion_error"] <= r["terminal_tv"]+1e-12
        and r["terminal_tv"] <= min(r["mean_path_tv_bound"],
                                   r["uniform_path_tv_bound"],r["kl_path_tv_bound"])+1e-12 for r in rows)
    lines = [
        r"\begin{tabular}{rrrrrr}", r"\toprule",
        r"$\theta$ & Depl. bias & Terminal TV & $L^1$ bound & KL bound & $|\Delta$CVaR$_{.99}|/B$ \\",
        r"\midrule"]
    for r in rows:
        lines.append(f'{r["theta"]:.3f} & {r["depletion_error"]:.5f} & '
                     f'{r["terminal_tv"]:.5f} & {r["mean_path_tv_bound"]:.5f} & '
                     f'{r["kl_path_tv_bound"]:.5f} & '
                     f'{r["cvar99_bound_over_B"]:.5f} ' + r"\\")
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    (ROOT/"tables/queue.tex").write_text("\n".join(lines)+"\n")
    m = np.array([2, 4, 8, 16, 32, 64, 128, 256])
    beta, eta, K = .04, .06, .4
    sums = np.array([np.sum(np.arange(1, int(j)+1, dtype=float)**-2) for j in m])
    tail2 = zeta(2, 1)-sums
    fitting2 = (beta**2+eta**2)*sums
    kappa = np.sqrt(tail2+fitting2)
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.6), layout="constrained")
    ax[0].plot(theta_values, [r["terminal_tv"] for r in rows], "o-", color=BLUE,
               label="Terminal distribution TV")
    ax[0].plot(theta_values, [r["depletion_error"] for r in rows], "s-", color=GREEN,
               label="Depletion probability error")
    ax[0].plot(theta_values, [r["mean_path_tv_bound"] for r in rows], "^-",
               color=RED, label="L¹ path upper bound")
    ax[0].plot(theta_values, [r["kl_path_tv_bound"] for r in rows], "d-",
               color=GREY, label="KL / Pinsker path bound")
    ax[0].set(xlabel="Relative death-rate error θ", ylabel="Probability / TV",
              title="Exact finite-state calculation")
    ax[0].legend(fontsize=8)
    ax[1].loglog(m, np.sqrt(tail2), "o-", color=GREY, label="Unresolved field tail")
    ax[1].loglog(m, kappa, "s-", color=BLUE, label="Exact posterior W₂")
    ax[1].loglog(m, K*kappa, "^-", color=RED, label="Local rate-error bound")
    ax[1].axhline(np.sqrt((beta**2+eta**2)*zeta(2, 1)), color=BLUE, ls=":", alpha=.6)
    ax[1].set(xlabel="Retained field coordinates", ylabel="Error / bound",
              title="Resolution and conditional fit")
    ax[1].legend()
    save(fig, "event_error_certificate.png")
    return {"horizon": T, "initial_queue": initial,
            "expected_death_count": expected_death_count,
            "true_depletion_probability": float(p[0]), "rows": rows,
            "resolution": {"m": m.tolist(), "beta": beta, "eta": eta, "K": K,
                           "kappa": kappa.tolist(), "rate_bound": (K*kappa).tolist(),
                           "limiting_kappa": float(np.sqrt((beta**2+eta**2)*zeta(2, 1)))}}

def execution_geometry():
    prices = np.array([100, 100.01, 100.03, 100.06])
    q = np.array([2., 3., 2., 3.])
    qhat = np.array([1., 2., 4., 3.])
    mass = q.sum()
    u = np.linspace(0, mass, 1001)
    def cost(volumes):
        left = np.r_[0, np.cumsum(volumes)[:-1]]
        return (np.clip(u[:, None]-left, 0, volumes)*(prices-prices[0])).sum(axis=1)
    c, chat = cost(q), cost(qhat)
    bound = mass*wasserstein_distance(prices, prices, u_weights=q, v_weights=qhat)
    checks["execution_quantile_bound"] = bool(np.max(np.abs(c-chat)) <= bound+1e-12)
    checks["execution_bound_attained"] = float(abs(abs(c[-1]-chat[-1])-bound))
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.5), layout="constrained")
    positions = np.arange(4)
    ax[0].bar(positions-.18, q, width=.36, color=BLUE, label="Book A")
    ax[0].bar(positions+.18, qhat, width=.36, color=RED, label="Book B")
    ax[0].set_xticks(positions, [f"{p:.2f}" for p in prices])
    ax[0].set(xlabel="Ask price", ylabel="Lots", title="Equal mass, displaced liquidity")
    ax[0].legend()
    ax[1].plot(u, c, color=BLUE, lw=2, label="Book A")
    ax[1].plot(u, chat, color=RED, lw=2, label="Book B")
    ax[1].fill_between(u, c, chat, color=RED, alpha=.13)
    ax[1].set(xlabel="Quantity bought", ylabel="Cost above buying at 100",
              title=f"Terminal cost gap = M W₁ = {bound:.3f}")
    ax[1].legend()
    save(fig, "execution_geometry.png")
    return {"prices": prices.tolist(), "volume_a": q.tolist(), "volume_b": qhat.tolist(),
            "mass": float(mass), "transport_cost_bound": float(bound),
            "terminal_cost_gap": float(abs(c[-1]-chat[-1]))}

def pricing():
    spot, sigma, weights = 100.0, np.array([.15, .35]), np.array([.5, .5])
    strikes = np.linspace(60, 140, 401)
    maturities = np.array([.25, .5, 1., 2.])
    curves = []
    for T in maturities:
        v = sigma[:, None]*np.sqrt(T)
        d1 = (np.log(spot/strikes)[None, :] + .5*v*v)/v
        curves.append(weights @ (spot*norm.cdf(d1)-strikes[None, :]*norm.cdf(d1-v)))
    curves = np.array(curves)
    checks["call_strike_monotonicity"] = bool(np.diff(curves, axis=1).max() < 1e-10)
    checks["call_strike_convexity"] = bool(np.diff(curves, n=2, axis=1).min() > -1e-10)
    checks["call_calendar_monotonicity"] = bool(np.diff(curves, axis=0).min() > -1e-10)
    t = np.linspace(0, 2, 200)
    uncorrected = spot*(weights[:, None]*np.exp(.5*sigma[:, None]**2*t)).sum(axis=0)
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.5), layout="constrained")
    for T, c in zip(maturities, curves):
        ax[0].plot(strikes, c, lw=2, label=f"T = {T:g}")
    ax[0].set(xlabel="Strike", ylabel="Call price", title="Exact mixture prices")
    ax[0].legend()
    ax[1].plot(t, uncorrected, color=RED, lw=2, label="Uncorrected log innovations")
    ax[1].axhline(spot, color=BLUE, lw=2, label="Martingale construction")
    ax[1].set(xlabel="Time", ylabel="Expected discounted stock",
              title="The conditional drift correction")
    ax[1].legend()
    save(fig, "martingale_pricing.png")
    return {"spot": spot, "volatilities": sigma.tolist(), "weights": weights.tolist(),
            "maturities": maturities.tolist(),
            "atm_calls": curves[:, np.argmin(abs(strikes-spot))].tolist(),
            "uncorrected_mean_at_2": float(uncorrected[-1]),
            "corrected_mean_at_2": spot}

def reserve_check():
    errors, feasible = [], True
    count = 0
    for D in range(7):
        for H in range(7):
            for q in range(D+1):
                for r in range(H+1):
                    newD, newH = D-q+r, H-r
                    errors.append(abs((newD+newH)-(D+H-q)))
                    feasible &= (newD >= 0 and newH >= 0)
                    count += 1
    checks["reserve_conservation_max_error"] = max(errors)
    checks["reserve_nonnegative"] = bool(feasible)
    return count

if __name__ == "__main__":
    results = {"kind": "Synthetic illustrations; no trained neural models or real market data",
               "filter": filtering(), "queue": queue_and_resolution(),
               "execution": execution_geometry(), "pricing": pricing(),
               "reserve_states_checked": reserve_check(),
               "checks": checks, "environment": {
                   "python": platform.python_version(), "numpy": np.__version__,
                   "scipy": scipy.__version__, "matplotlib": matplotlib.__version__}}
    for name, value in checks.items():
        if isinstance(value, bool):
            assert value, name
        else:
            assert value < 1e-10, (name, value)
    (ROOT/"results/metrics.json").write_text(json.dumps(results, indent=2)+"\n")
    print(json.dumps(results, indent=2))
