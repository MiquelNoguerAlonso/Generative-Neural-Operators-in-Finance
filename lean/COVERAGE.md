# Formalization coverage

**Verified theorem declarations: 40.** This includes supporting lemmas. The refinement module appears in both standalone projects.

The Lean build and per-theorem axiom audit pass. There are no admitted proofs or custom mathematical axioms. This is a partial formalization of the manuscript, with the exact scope below.

## Manuscript correspondence

| Manuscript component | Formal coverage and boundary |
| --- | --- |
| Structural validity and reserve conservation | Executable reserve arithmetic and replay conservation checked. Complete venue matching and continuous-time support theorem are not mechanized. |
| Observable intensity and hidden-state filter | Written proofs only; compensators, Bayesian likelihoods, and measurable posteriors are not mechanized. |
| Snapshot obstruction | Written probability-law proof; a general metric analogue is present in the first project. |
| Cell integration lemma | Finite quadrature L1 contraction and weighted L2 bound checked. General integration over a measure space is a written proof. |
| Posterior-intensity and path comparison theorems | Written proofs only; transport couplings and common-Poisson construction are not mechanized. |
| Posterior refinement certificate | Real-sequence core checked; the stochastic coupling and infinite-dimensional interpretation are written proofs. |
| Sweep-cost transport theorem | Discrete prefix inequality checked; sorted quantile interpretation and optimal W1 identity are written proofs. |
| Bounded execution risk | Full finite-law bounded payoff and indicator inequalities checked; general path-space extension is a written proof. |
| CVaR, VaR, unbounded-cost statements | Finite CVaR auxiliary-objective bound checked. Taking an infimum, the VaR counterexample, and Holder extension are written proofs. |
| Policy regret | Universal value-function comparison checked, conditional on a uniform value-error premise; causal identification is not supplied. |
| Martingale pricing | Finite categorical normalization and one-step mean preservation checked. Gaussian exponential moments, the general martingale, option-price shape, and adapted volatility-to-price theorem are written proofs. |

## Every checked declaration

| Declaration | Source | Exact checked claim |
| --- | --- | --- |
| FinGNO.cell_integration_contraction | FinGNO/CellRates.lean | Finite weighted cell aggregation contracts the weighted absolute field error. |
| FinGNO.weighted_l1_square_bound | FinGNO/CellRates.lean | Squared weighted Cauchy-Schwarz bound with reference-mass constant. |
| FinGNO.weighted_l1_l2_bound | FinGNO/CellRates.lean | Weighted L1 to L2 bound, including zero quadrature weights. |
| FinGNO.prefix_cost_error | FinGNO/Execution.lean | Partial sums of price differences are bounded by the full sum of absolute differences; identification with quantile W1 is external. |
| FinGNO.policy_regret | FinGNO/Execution.lean | Uniform value error and approximate model optimality imply the 2-error-plus-optimization-error comparison against every policy. |
| FinGNO.cvar_objective_error | FinGNO/Execution.lean | Finite-law CVaR auxiliary-objective bound, before the infimum over thresholds. |
| FinGNO.tv_nonneg | FinGNO/FiniteLaws.lean | Nonnegativity of half-L1 total variation of finite probability laws. |
| FinGNO.tv_symm | FinGNO/FiniteLaws.lean | Symmetry of finite-law total variation. |
| FinGNO.tv_triangle | FinGNO/FiniteLaws.lean | Triangle inequality for finite-law total variation. |
| FinGNO.bounded_expectation_error | FinGNO/FiniteLaws.lean | Exact range-B expectation bound B times total variation for finite probability laws. |
| FinGNO.event_probability_error | FinGNO/FiniteLaws.lean | Finite event-probability discrepancy is bounded by total variation. |
| FinGNO.positive_expectation | FinGNO/Pricing.lean | Every strictly positive finite score has strictly positive expectation under a finite probability law. |
| FinGNO.normalized_return_positive | FinGNO/Pricing.lean | Every normalized finite return is strictly positive. |
| FinGNO.normalized_return_mean_one | FinGNO/Pricing.lean | Normalized finite returns have expectation exactly one. |
| FinGNO.normalized_step_mean | FinGNO/Pricing.lean | Multiplication by a normalized finite return preserves the current stock mean. |
| FinGNO.radius_nonneg | FinGNO/Refinement.lean | The recursively defined real radius is nonnegative at every depth. |
| FinGNO.radius_sq_succ | FinGNO/Refinement.lean | The square-root definition satisfies the exact squared recurrence. |
| FinGNO.radius_monotone | FinGNO/Refinement.lean | The radius is nondecreasing with the number of retained bands. |
| FinGNO.square_step_monotone | FinGNO/Refinement.lean | The squared update is monotone on nonnegative errors for nonnegative fitting error and sensitivity. |
| FinGNO.error_le_radius | FinGNO/Refinement.lean | Every nonnegative discrepancy sequence satisfying the one-step squared bound lies below the radius. |
| FinGNO.radius_step_bound | FinGNO/Refinement.lean | The nonlinear squared step is bounded by its linear majorant step. |
| FinGNO.radius_sq_le_linearBound | FinGNO/Refinement.lean | The radius squared lies below the recursively defined linear majorant. |
| FinGNO.context_independent_exact | FinGNO/Refinement.lean | Zero context sensitivity gives the exact sum of squared fitting errors. |
| FinGNO.exponential_certificate | FinGNO/Refinement.lean | Universal finite exponential bound on the radius squared. |
| FinGNO.add_tail_certificate | FinGNO/Refinement.lean | Algebraic consequence of a supplied orthogonal square decomposition and projected square bound. |
| FinGNO.accepted_event_conserves | FinGNO/Reserve.lean | Every accepted executable reserve update conserves total inventory after accounting for executed quantity. |
| FinGNO.accepted_replay_conserves | FinGNO/Reserve.lean | Every accepted finite reserve-event replay conserves inventory after cumulative executions. |

## Decision-specific control extensions

| Declaration | Checked statement | Boundary |
|---|---|---|
| FinGNO.rate_box_endpoints | Sign-dependent lower and upper rate-box products | Real interval algebra |
| FinGNO.pessimistic_policy_regret | Selected-policy comparison with twice the comparator's own radius | Simultaneous uncertainty event is a hypothesis |
| FinGNO.expectation_monotone | Monotonicity for actual finite probability laws | Finite outcomes |
| FinGNO.expectation_sup_error | Sup-norm nonexpansiveness of probability-weighted expectation | Finite outcomes |
| FinGNO.finite_robust_sandwich | Bellman subsolution bounds every policy; supersolution bounds the selected policy | Actual recursive finite-horizon policy laws; discrete time |
| FinGNO.finite_horizon_residual | Local Bellman residuals accumulate additively | Discrete time; no floating-point enclosure |

The continuation identity, counting-process confidence sequences, continuous-time HJB comparison and residual estimate, and bicausal stopping theorem remain written proofs. No claim of full analytic formalization follows from the finite analogue.

## Trust and reproduction

The statements use exact real numbers and finite types, not floating-point experiments. Standard library foundations are reported for every theorem in axioms.log. verification.json records their axiom sets and the SHA-256 of each checked source file and project configuration.

Hypotheses appear in the Lean declarations as hypotheses; they are not disguised as proofs. Probabilistic and analytic constructions excluded above remain explicitly written proofs in the manuscript. A theorem declaration in this project is never an assertion that every result in its associated paper section has been mechanized.

## Added finite histories and thinning interface

| Declaration | Checked statement | Analytic boundary |
|---|---|---|
| FinGNO.joint_tv_same_base | Exact conditional TV identity with a common history law | Finite normalized laws |
| FinGNO.joint_tv_same_kernel | Appending a common kernel preserves history TV | Finite normalized laws |
| FinGNO.joint_tv_bound | True-history-weighted conditional kernel discrepancy bound | Finite marks |
| FinGNO.joint_tv_uniform | Uniform next-mark error bound | Finite marks |
| FinGNO.history_tv_bound | Full finite-history law discrepancy bounded by accumulated kernel errors | Discrete steps; not continuous event-time paths |
| FinGNO.posterior_acceptance_probability | The mixture acceptance probability is in [0,1] | Finite posterior |
| FinGNO.posterior_thinning_rate | Proposal rate times mixture acceptance equals posterior-averaged rate | Marked-Poisson compensator proof remains in the manuscript |

The normalized joint and recursive history laws are constructed in the module, not supplied as unproved assumptions. The expected posterior-TV stability proposition, KL likelihood argument, and adapted volatility perturbation theorem remain analytic.
