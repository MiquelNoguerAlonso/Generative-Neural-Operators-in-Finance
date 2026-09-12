# Technical assessment of the expanded generative neural operator papers

**Author:** Miquel Noguer i Alonso. **Assessment date:** September 12, 2026.

**Paper I:** *The Mathematics of Generative Neural Operators: Resolution Consistency, Conditional Refinement, and Hidden-State Obstructions*. DOI: [10.5281/zenodo.22714854](https://doi.org/10.5281/zenodo.22714854).

**Paper II:** *Generative Neural Operators in Finance: Hidden Liquidity, Valid Market Simulation, and Execution Guarantees*. DOI: [10.5281/zenodo.22714857](https://doi.org/10.5281/zenodo.22714857).

This assessment covers the 49-page foundations manuscript and 42-page finance manuscript, complete source packages, numerical experiments, saved models, and Lean projects. The same assistant developed the revisions and performed this assessment. It is an internal technical review, not an independent referee report; the filename is retained to preserve the existing review artifact.

## 1. Grade and meaning of the assessment

**Internal manuscript-quality grade: A+ for both, within their stated scope as mathematical methods papers with reproducible synthetic validation and partial formalization.** This is a qualitative assessment of specification, proof development, breadth, reproducibility, and the accuracy of the claims. It is not an established research-priority verdict, a claim of complete Lean verification, an empirical market-performance rating, or a guarantee of publication.

The upgrade is supported by substantive work. Paper I now estimates conditional-law discrepancy from observed samples without evaluating a target conditional mean, proves a dependency-sensitive propagation theorem, and treats nonorthogonal and nonlinear representations. Paper II now derives confidence intervals from recorded events and exposures, connects them to data-selected execution policies, accounts for control-solver discretization, and addresses early exercise through information-preserving transport. Both projects mechanize additional universal mathematics.

| Assessment dimension | Paper I | Paper II |
|---|---|---|
| Mathematical specification and proof exposition | A+ | A+ |
| Breadth and connection between results | A+ | A+ |
| Reproducibility within the documented environment | A+ | A+ |
| Integrity and disclosure of Lean coverage | A+ | A+ |
| Experimental support for the stated synthetic claims | A | A |
| Independent assessment of originality and priority | Still required | Still required |
| External financial calibration or benchmark superiority | Not claimed | Not established |
| Internal manuscript-quality judgment | **A+** | **A+** |

The experimental grade remains lower than the technical manuscript grade for a reason: the new guarantees are valid under explicit model assumptions, but several are substantially wider than the measured errors. The finance study uses synthetic observations rather than exchange records. These limitations are documented rather than erased to reach a desired label. The previous research grades and this scoped manuscript-quality assessment should not be read as scores on an identical objective scale.

## 2. Findings resolved by the deeper revision

| Earlier limitation | New result or evidence | Remaining boundary |
|---|---|---|
| Conditional validation required a known target mean | Two-split observed-sample conditional-law certificate | Bounded scalar details, sufficient context, regularity, and a justified tail envelope |
| Orthogonal physical observations were central | Riesz-coordinate certificate and bi-Lipschitz decoder transfer | Compatible invertible representation; arbitrary noninjective sensors remain outside the result |
| A generic context radius obscured actual architecture | Dependency-sensitive triangular propagation theorem | Coordinatewise sensitivities must hold globally on relevant contexts |
| Optimal gain was entirely a written calculation | Lean checks the exact 2x2 spectral bound and nonzero attainment | Complete hierarchy attainment and infinite-product necessity remain analytic |
| Learned finance rates used known synthetic rate labels | A separate network trains on event counts and exposures by likelihood | Observable finite Markov state and homogeneous conditional rates |
| Policy bounds could pay for economically irrelevant errors | Exact continuation-value sensitivity identity | True occupancy must be retained or replaced by a valid upper bound |
| Policy selection lacked a data-derived uncertainty event | Time-uniform rate boxes and robust policy comparison | Adequate action coverage and correct intensity representation |
| A numerical HJB output was not an exact solution | Additive residual allowance and independent policy evaluation | Floating-point and quadrature rounding are not formally enclosed |
| Terminal pricing did not address early exercise | Bicausal stopping-value bound and information-timing counterexample | Shared simulation innovations alone do not establish bicausality |

The prior corrections also remain in place: quiet intervals update hidden-state beliefs; fresh posterior draws at thinning proposals implement the asserted observable rate; reserve updates preserve inventory; physical and pricing laws are separated; projected laws and pathwise sample consistency are distinguished; and both papers contain their required proofs locally without citing the author's draft papers.

## 3. Paper I: mathematical assessment

### 3.1 The central recurrence and its sharp class-wide gain

The paper's strongest central connection is between conditional fitting, the geometry of appending an orthogonal detail, and existence of an infinite generated field. Its recurrence is

$$d_{-1}=0,\qquad d_j^2=d_{j-1}^2+(\varepsilon_j+L_jd_{j-1})^2.$$

The proof couples old contexts, transports the true detail to the learned detail at the true context, and then changes the learned context. Minkowski controls the new-detail error, while orthogonality adds its square to the retained-context cost. This avoids charging all errors by an ordinary sum. At zero sensitivity the result reduces to the exact quadrature of fitting errors.

The optimal aggregate-energy constant is determined by

$$g_0=1,\quad A_j=(1+L_j^2)g_{j-1},\qquad
 g_j=\frac{A_j+1+\sqrt{(A_j-1)^2+4L_j^2g_{j-1}}}{2}.$$

It bounds $d_m^2$ by $g_m\sum_{j\le m}\varepsilon_j^2$. The proof establishes both an upper bound and attainment, including diagonal degeneracies. Nonnegative attaining error vectors are lifted to deterministic conditional kernels, so sharpness concerns the stated kernel class and not merely a scalar numerical recurrence.

The threshold

$$\sup_m g_m<\infty\quad\Longleftrightarrow\quad\sum_{j\ge1}L_j^2<\infty$$

is carefully scoped. Necessity follows by placing all fitting error in the first band, obtaining the exact product $\prod_{j=1}^m(1+L_j^2)$. It is a condition for uniform robustness over the whole class; it is not a necessary condition for every individual architecture to behave well. The dependency theorem makes that distinction constructive.

The exact tail identity and summability argument remain essential. Projective consistency by itself does not establish finite Hilbert energy. The paper supplies the additional second-moment argument before asserting almost-sure and mean-square convergence.

### 3.2 Nonorthogonal observations: what transfers and what does not

For a bounded invertible linear representation $A$ with

$$a\|z\|^2\le\|Az\|^2\le b\|z\|^2,$$

coefficient truncation induces the generally oblique physical projection $AQ_mA^{-1}$. The certificate is exact in the pulled-back coefficient metric and is bracketed in the physical metric by $a$ and $b$. The proof correctly maps every coupling in both directions; an upper pushforward argument alone would not establish the lower comparison.

The constants are optimal by Dirac pairs approaching extremal Rayleigh quotients. The explicit Gram matrix with diagonal entries one and off-diagonal overlap $c$ demonstrates the missing cross term. Its forward upper distortion remains below two as $|c|$ approaches one, while inverse conditioning diverges. These are distinct conclusions, and the figure treats them separately.

The nonlinear extension is deliberately limited to a measurable bi-Lipschitz representation with a measurable inverse. The induced observation is $FQ_mF^{-1}$, not an arbitrary physical sensor. A Lipschitz noninjective decoder transfers an upper distance bound but does not automatically define an inverse observation hierarchy. This is a sound geometric extension rather than an unsupported assertion of general nonlinear Pythagoras.

### 3.3 Observed-sample certification: the actual probability argument

For scalar laws supported on an interval of diameter $D$,

$$W_2^2(P,Q)\le D W_1(P,Q)\le D^2\|F_P-F_Q\|_\infty.$$

The DKW--Massart inequality therefore supplies a conservative empirical transport radius of order $D(\log(1/\alpha)/n)^{1/4}$. This is a standard concentration ingredient, properly attributed, not claimed as an original inequality.

The new contribution within the manuscript is a complete audit interface for the conditional hierarchy. A predeclared sufficient feature is partitioned into cells. The first independent split estimates each cell's mixture detail law; the second estimates the target-weighted average of the resulting squared radii. The proof accounts for five issues that can otherwise invalidate such an audit:

1. **Random cell counts.** Conditional on a positive count, the selected details have the cell-conditional distribution. Averaging the conditional failure statement preserves its budget.
2. **Within-cell bias.** Target and learned kernel Lipschitz constants control movement from a target feature to the cell mixture and from a representative to the learned kernel.
3. **Empty cells.** Their radius is the support diameter. The procedure does not treat absent observations as evidence of zero error.
4. **Dependence created by calibration.** An independent aggregation split is used. Calibration counts are not reused as if they were independent averaging weights.
5. **Selection after auditing.** The union event covers all predeclared candidates, detail bands, and cutoffs. The experiment additionally budgets across its three sample sizes.

The sufficient-feature condition is substantive. Replacing a full prefix by an arbitrary learned summary changes the target conditional law unless sufficiency is justified. The displayed statistical rate depends on this feature dimension. The proof gives a rate for the proposed audit, not an unproved minimax claim.

The unseen-cell proposition supplies a matching conceptual boundary. On an event of probability $(1-p)^N$, two targets differing only in a mass-$p$ cell produce identical data. Their squared conditional fitting errors against a common output sum to at least $pD^2/2$. A procedure always reporting a bound below $pD^2/4$ must therefore fail for at least one target with the stated probability. The revised wording allows a procedure to issue a wider bound or decline certification, which is necessary for the lower-bound claim to be precise.

### 3.4 Dependency-sensitive propagation is a material improvement

If the learned detail kernel satisfies

$$W_2(\widehat K_j(x),\widehat K_j(y))\le\sum_{i<j}b_{ji}\|x_i-y_i\|,$$

then the coupled coordinate discrepancies are bounded by

$$a_0=\varepsilon_0,\qquad a_j=\varepsilon_j+\sum_{i<j}b_{ji}a_i,$$

and the full-law squared radius is the tail energy plus $\sum_j a_j^2$. The proof retains previously constructed coordinate couplings and applies Minkowski before orthogonal aggregation. It does not infer a joint coupling from separately optimized marginal distances without justification.

The finite inverse $(I-B)^{-1}=I+B+\cdots+B^m$ reveals sensitivity products along dependency paths. Its infinite counterpart is not assumed bounded merely because every finite inverse exists. If all details use only an exactly sampled first coordinate, no generated-context discrepancy propagates, even when the ordinary prefix Lipschitz constant is positive.

In the observed-data experiment this changes a 32-mode bound from **0.908405 to 0.585551**, with identical data, model, support assumptions, and confidence level. The no-context bound is **0.723932**. The improvement is therefore attributable to the proved architectural restriction, rather than post hoc relaxation of coverage.

### 3.5 Experimental evidence and its practical limit

The original Gaussian conditional experiment remains useful because it exposes conditional mean and scale errors directly. It trains three 37-parameter shared spectral networks and evaluates a separate context ablation. Its known conditional mean is used in the audit, not as a training label.

The additional bounded-detail experiment trains three 24-parameter networks on 16,384 noisy fields through eight modes. Two independent audit splits cover 31 detail bands through mode 32. The support envelope, known noise scale, target regularity, sufficient first coordinate, and infinite tail envelope are all stated.

| Observed fields per audit split | Cells | Seed-481 full-law bound | No-context bound |
|---:|---:|---:|---:|
| 4,096 | 8 | 1.030396 | 1.063198 |
| 16,384 | 12 | 0.765316 | 0.868702 |
| 65,536 | 16 | 0.585551 | 0.723932 |

At the largest budget, the three trained bounds range from 0.585268 to 0.587704. A separate truth diagnostic evaluates a specified full-law coupling at approximately 0.0633 for the first seed. It is not an optimal Wasserstein distance and does not enter the audit. The gap shows that observed-data certification is possible under the assumptions but remains conservative. The paper does not disguise this gap as evidence of tight uncertainty estimation.

## 4. Paper II: mathematical and financial assessment

### 4.1 The latent-field-to-event chain remains correctly specified

The original path comparison links posterior Wasserstein error and conditional field error to integrated observable-intensity discrepancy, then to the law of the entire event path. Integration over physical cells yields a square-root reference-mass constant, avoiding an arbitrary dependence on the number of numerical cells. The comparison uses a common admissible transition mechanism and does not require depletion or matching to be Lipschitz in a continuous field norm.

The posterior sampler draws a fresh latent state at each thinning proposal. The conditional acceptance rate is exactly the posterior-averaged intensity. Quiet intervals update the posterior through survival likelihood, while rejected internal proposals are excluded from observed history. Holding a single average rate fixed through quiet intervals would generally produce a different survival law; the paper explicitly demonstrates that distinction.

The full hidden reserve experiment still trains on a finite synthetic rate table. That evidence is retained and labelled as finite-domain emulation. It is complemented by, rather than confused with, the new event-count-trained observable control example.

### 4.2 Continuation values connect error to economic relevance

For a common policy and common cost specification, the exact identity is

$$V_\lambda^\pi-\widehat V^\pi
 =\mathbb E_\lambda^\pi\int_0^T\sum_e(\lambda_e-\widehat\lambda_e)\Gamma_e^\pi\,dt,$$

where $\Gamma_e^\pi$ includes the mark cost and learned continuation-value change. Subtracting the learned backward equation from the true Dynkin/compensator calculation proves the identity. The same learned value is used consistently throughout.

A critical point is that the occupancy is the true occupancy. Replacing it by a learned occupancy without correction would change the claim. The paper instead gives a computable statewise maximum bound. An event with zero continuation increment contributes zero to this identity, explaining why a universal payoff-range bound may be unnecessarily expensive.

For the tested fixed passive policy, the continuation bound is **0.469600**, compared with **5.071310** for the payoff-range/path-TV route using the same rate intervals: a factor of about **10.80**. The actual signed cost difference is approximately −0.00904582. Numerical integration of the signed identity agrees within $4.82\times10^{-9}$. The weighted bound remains conservative, and its numerical quadrature is not presented as an interval enclosure.

### 4.3 Confidence sequences use actual event data

For each state-action-mark triple, the model specifies compensator $\lambda_i E_i(t)$ for count $N_i(t)$. The exponential

$$\exp\{\eta N_i(t)-(e^\eta-1)\lambda_i E_i(t)\}$$

is a nonnegative local martingale and hence a supermartingale. Applying Ville's inequality to both signs of a finite predeclared grid, then taking a union bound over triples and grid points, gives the displayed interval endpoints simultaneously for all times. This is an application of established time-uniform inference, with its provenance acknowledged.

The probability budget includes the grid size. Adaptive predictable actions and data-dependent stopping do not invalidate the event. Empty exposure receives the full envelope. An empty computed intersection is reported as inconsistent rather than silently repaired. None of this identifies a hidden state or supplies an unobserved exposure clock.

The three synthetic streams use 2,000, 8,000, and 32,000 episode prefixes. Their networks train by exposure-weighted likelihood without oracle rate labels. The experiment records every count, exposure, endpoint, raw neural rate, and clipped deployed rate. Thus the statistical statement has inspectable observed inputs.

### 4.4 Robust selection and solver error are both covered

Rectangular rate boxes define upper and lower Hamiltonians. The lower value is a subsolution for every admissible action, while the upper value is a supersolution for the action selected by the robust minimization. Dynkin's identity yields

$$L\le V_\lambda^*\le V_\lambda^{\pi^+}\le U.$$

The rate confidence event is simultaneous before selection, so a fitted policy is covered. Rectangularity is an enlargement of uncertainty and can be conservative when parameters are shared across states. The paper acknowledges this rather than interpreting the width as irreducible market uncertainty.

For explicit Euler control, the piecewise-linear residual is bounded using the Hamiltonian's $2\Lambda$ Lipschitz constant. Translation invariance and comparison accumulate the integrated residual additively, without an unnecessary exponential Gronwall factor. The same argument covers the grid-selected policy interpreted in continuous time. The regret allowance includes both upper and lower residuals.

| Episodes | Mean nominal neural regret | Mean robust regret | Largest 99% regret bound across streams |
|---:|---:|---:|---:|
| 2,000 | 0.00214 | 0.02138 | 1.0618 |
| 8,000 | 0.00014 | 0.00657 | 0.4681 |
| 32,000 | 0.00004 | 0.00161 | 0.2341 |

The nominal neural policy performs better in these realized synthetic cases. Reporting that fact is necessary: the evidence establishes a valid uncertainty-aware policy certificate, not uniform realized superiority of pessimism. At 32,000 episodes the robust regrets lie between 0.001178 and 0.001968, far below their conservative bounds.

Policy costs are evaluated by matrix exponentiation over intervals with identical action vectors. A separate high-accuracy ODE computation provides the known-model optimum. Doubling the control grid changes the initial upper value by $7.32\times10^{-5}$, while the residual allowance roughly halves from 0.004900 to 0.002450. These are meaningful independent calculations within the synthetic model, not substitutes for exchange-data validation.

### 4.5 Early exercise requires information preservation

The pricing extension correctly distinguishes martingale structure, terminal calibration, and stopping decisions. Under a bicausal coupling, an exercise rule for one process projects to a randomized stopping rule for the other. Finite-date Snell-envelope induction shows that independent randomization cannot improve its optimal stopping value. Reversing the coupling's causality direction yields the absolute value bound by the expected maximum path discrepancy.

The counterexample has identical terminal discounted-stock laws, but one model reveals the outcome at date one and the other at date two. Both are martingales. At interest rate 0.1, their American put values are 0.452419 and 0.409365; their European values coincide. Zero terminal transport distance therefore does not control early exercise.

This is a correct use of established adapted-transport ideas. Shared innovations in an enlarged simulation filtration do not automatically yield a bicausal coupling for the observed price filtrations. The paper states that restriction explicitly.

## 5. Lean: what was actually checked

Both projects build under Lean 4.19.0 with an exact mathlib dependency manifest. The verification scripts enumerate every theorem, compile the project, audit axiom dependencies, and record source hashes. There are no admitted proofs or custom mathematical axioms. The allowed logical dependencies are propositional extensionality, classical choice, and quotient soundness where used.

| Project | Previous declarations | Current declarations | Principal extensions |
|---|---:|---:|---|
| Foundations | 25 | **35** | Exact spectral bound and attainment; dependency recursion; Gram distortion; finite metric transfer; unseen-cell squared-loss bound |
| Finance | 34 | **40** | Rate endpoints; comparator-specific regret; finite probabilistic Bellman sandwich; additive residual control |

The 75 declarations include supporting lemmas and ten refinement declarations duplicated between the standalone projects. They are not 75 distinct new contributions or a count of fully mechanized manuscript theorems.

The foundations spectral module now checks a central optimization step rather than only a numerical special case. Its attaining vector is nonzero even in diagonal degeneracies. The dependency module uses well-founded recursion over all earlier coordinates. The observation module operates on actual normalized finite probability laws where appropriate.

The finance control module recursively defines finite-horizon policy values from normalized transition laws, then proves subsolution/supersolution comparison and residual accumulation. These statements are finite probabilistic analogues. They do not encode a continuous-time compensator, a Poisson construction, or the HJB ODE itself.

Disintegration, measurable optimal-coupling selection, Hilbert limits, concentration theorems, continuous-time filtering and control, and bicausal stopping remain written proofs. The coverage maps and manuscript explanations agree on these boundaries. Float64 execution is also separate from exact Lean mathematics.

## 6. Reproduction, citation, and artifact audit

The two new experiments were rerun from their programs. Their result JSON files, trained model files, numerical tables, and figure files reproduced exactly in the documented environment. These checks supplement the earlier exact reruns of five original result reports. All seven numerical result reports now have executed reproduction evidence; both final Lean audits pass.

| Final artifact measure | Foundations | Finance |
|---|---:|---:|
| PDF pages | 49 | 42 |
| Theorem environments | 13 | 13 |
| Proposition environments | 4 | 11 |
| Corollary environments | 5 | 1 |
| Lemma environments | 0 | 2 |
| Written proof environments | 22 | 27 |
| PNG figures | 7 | 6 |
| Tables, including formal coverage | 6 | 4 |
| Bibliography entries | 27 | 20 |
| Checked Lean declarations | 35 | 40 |

Both documents follow the author's established academic LaTeX format: an 11-point article, 1.08-inch margins, 1.08 line spacing, indented paragraphs without added paragraph spacing, classic serif typography, and the Miquel Noguer i Alonso / AIFI author block. After the abstract and keywords, each paper includes a two-page clickable table of contents covering sections and subsections, the formalization material, and references. The contents and main text start on fresh pages. Running headers, footers, and printed page numbers remain omitted. The physical PDF page counts above include the contents and complete references. The standing format is recorded in `Academic_LaTeX_Format.md` in both source packages.

Both documents use `natbib`, `plainnat`, and an actual `\date{\today}` command. Each opening page displays the associated DOI below the date, with a clickable DOI link and matching PDF metadata. Neither bibliography contains an author self-citation or a citation to either draft paper. The DOI links in this review identify the works assessed; they are not used to support the papers' mathematical claims. No replacement of the remote Zenodo deposits is asserted.

The complete PDFs compile without unresolved references or reported box warnings. The page layouts, new mathematics, figures, tables, and references were rendered for visual review. Every package includes its PDF, LaTeX, bibliography, figures, runnable programs, saved models, results, Lean sources, dependency manifests, build and axiom logs, declaration-level coverage, this review, and a SHA-256 inventory. Binary dependency caches are excluded.

## 7. Boundaries an external reviewer should retain

The revision closes the main internal specification and proof-interface gaps. It gives the foundations paper an observed-sample statistical component and gives finance a complete observable-data-to-policy certificate. That is the basis for the scoped A+ manuscript-quality judgment.

Three issues remain open scientific questions rather than defects to hide. First, the precise novelty and priority of the combined results need independent specialist assessment; familiar ingredients are explicitly attributed. Second, the statistical and robust-control certificates can be substantially conservative. Sharper uncertainty sets and a better treatment of low-dimensional sufficient information are plausible next contributions, not already established results. Third, external market calibration and causal action-response identification require suitable records and a defensible observation model. The present synthetic experiments do not supply them.

The papers are ready for serious independent technical evaluation within their stated scope. No internal grade can establish that both are groundbreaking publications in advance of that evaluation.
