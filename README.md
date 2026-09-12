# Generative Neural Operators in Finance

**Manuscript:** [Read the complete PDF](Generative_Neural_Operators_Finance.pdf)

**Author:** Miquel Noguer i Alonso

**DOI:** [10.5281/zenodo.22714857](https://doi.org/10.5281/zenodo.22714857)

**Subtitle:** Hidden Liquidity, Valid Market Simulation, and Execution Guarantees

The manuscript connects posterior field approximation and event-intensity errors to observable path laws, execution probabilities, bounded costs, tail risk, and policy regret. It includes hidden-liquidity filtering, valid reserve updates, liquidity-quantile geometry, and a separate adapted martingale pricing construction with a volatility-to-price error estimate.

## Compile

The main document is Generative_Neural_Operators_Finance.tex. It uses natbib author-year citations and the plainnat bibliography style. All six figures are PNGs and are already included.

~~~bash
latexmk -pdf -interaction=nonstopmode -halt-on-error Generative_Neural_Operators_Finance.tex
~~~

Alternatively run pdfLaTeX, BibTeX, and pdfLaTeX twice. For Overleaf, upload the complete ZIP, select the main document above, and use pdfLaTeX. Lean and Python do not have to run to compile the manuscript.

## Numerical reproduction

~~~bash
python3 -m pip install -r requirements.txt
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 experiments/reproduce.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 experiments/learned_reserve.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 experiments/certified_control.py
~~~

The first program recreates four figures, the queue table, and results/metrics.json. The studies use a static-regime Poisson filter, exact finite-state matrix exponentials, analytic Gaussian posterior distances, a sharp sweep-cost example, and analytic mixture option prices. Eleven numerical and accounting checks pass. The reserve enumeration covers 784 admissible combinations.

The explicit calculations are accompanied by a complete learned-rate reserve model in experiments/learned_reserve.py. It trains a 746-parameter rate emulator, updates beliefs during quiet intervals and executions, implements both exact posterior averaging and fresh posterior randomization at thinning proposals, and values a finite execution class by matrix exponentiation. No real-market calibration or investment-performance claim is made.

## Lean reproduction

The lean directory is a standalone Lean 4.19.0 project using a pinned mathlib release and exact dependency manifest.

~~~bash
cd lean
lake exe cache get
python3 verify.py
~~~

Forty theorem declarations pass compilation and an axiom audit. They include finite probability and payoff results, weighted quadrature bounds, reserve transition and replay conservation, discrete sweep-cost bounds, policy comparison, a CVaR auxiliary-objective bound, finite martingale normalization, and the finite refinement certificate.

Read lean/COVERAGE.md and the formal-verification section for the exact correspondence with the paper. The continuous-time coupling, general measure-theoretic results, and Gaussian martingale construction are proved in the manuscript but are not completely mechanized. No result outside the stated formal scope is represented as a custom axiom.

## Package contents

- Main LaTeX document, complete sections, and references.bib.
- Six PNG figures and three generated numerical tables.
- Compiled PDF.
- experiments/reproduce.py and requirements.txt.
- experiments/learned_reserve.py and the portable parameters in models/reserve_rate_network.json.
- results/metrics.json with every reported number and verification result.
- results/learned_reserve.json with the complete model, policy, sampling, and adapted pricing results.
- results/revision_validation.json with the executed reproduction and proof-audit summary.
- lean project with source, dependency manifest, coverage map, build and axiom logs, and verification.json.

Valid market support, predictive calibration, latent identification, intervention-aware policy evaluation, and pricing under a chosen measure are separate claims throughout the paper.

## Complete learned reserve experiment

The rate network is trained on all 24 specified active state/action combinations with known synthetic rate labels. Every deployed input is enumerated to measure its field error and latent sensitivity. This is a finite-domain emulator audit, not an out-of-sample market-data study. Three conditioning histories are fixed in advance. All 32 deadline/action configurations are valued independently of the sampling check; the optimization is over that finite class, not unrestricted partial-observation control.

The exact model, weights, priors, filters, policy values, coupling and field/posterior bounds, and sampler diagnostics are in results/learned_reserve.json and models/reserve_rate_network.json. CPU float64 and deterministic single-threaded PyTorch are used. A separate 200,000-path paired experiment checks the adapted volatility-to-price bound. The queue example includes KL/Pinsker comparisons and nontrivial 99% CVaR error bounds.

The seven added Lean theorems construct normalized finite history laws, prove full-history TV accumulation, and check posterior acceptance probabilities and their rate identity. Continuous-time compensators and Poisson constructions remain written proofs; the finite-history result does not license rounding event times.

## Observed-event inference and robust execution

`experiments/certified_control.py` records counts and exposures from three synthetic observable-state streams, fits 74-parameter rate networks by likelihood without oracle rate labels, constructs time-uniform confidence boxes, and selects a robust policy. Three episode budgets are reported for every stream. The confidence event covers subsequent policy selection. Known synthetic rates are used only to generate data and evaluate diagnostic costs and coverage.

`results/certified_control.json` contains counts, exposures, interval endpoints, learned rates, policy values, continuation-weighted sensitivity, and time-grid residuals. `models/count_trained_rates.json` contains all nine trained models. The theorem's confidence and time-discretization allowance are evaluated in float64; no interval-arithmetic proof is claimed. Robust policies are compared with nominal neural policies, including the observed conservatism cost. A finite-date pricing example isolates early-exercise information timing.

Six additional Lean declarations check rate-box endpoints, comparator-specific policy regret, expectation monotonicity and nonexpansiveness, an actual finite probabilistic Bellman sandwich, and accumulation of local residuals. Counting-process confidence sequences, continuous-time control, and bicausal stopping remain written proofs.

## Standing academic LaTeX format

Use the author's established academic format for this and future papers: 11pt article; 1.08-inch margins; 1.08 line spacing; 1.25em paragraph indentation and no paragraph skip; small captions with bold labels; concealed link styling; natbib/plainnat; the Miquel Noguer i Alonso / Artificial Intelligence Finance Institute (AIFI) author block; and an actual `\today` date. The front matter includes a clickable table of contents covering sections and subsections, the appendix, and references. The contents and main text begin on fresh pages. Running headers, footers, and printed page numbers remain omitted. DOI links are separate title-page identifiers. `Academic_LaTeX_Format.md` records the reusable specification.
