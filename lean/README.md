# Lean companion

This project accompanies Generative Neural Operators in Finance.

The checked mathematical scope is defined by the statements in the Lean source and explained declaration by declaration in COVERAGE.md. The paper's analytic proofs are not silently assumed to have been formalized.

## Standard reproduction

Install Lean through the official elan distribution. This project requests Lean 4.19.0 through lean-toolchain. The lake manifest pins mathlib to commit c44e0c8ee63ca166450922a373c7409c5d26b00b and records the revisions of its dependencies.

From this directory:

~~~bash
lake exe cache get
lake build
lake env lean Audit.lean
~~~

The convenience verifier runs the build and audits every theorem:

~~~bash
python3 verify.py
~~~

It rejects admitted proofs and custom axiom declarations in the project source, verifies that Audit.lean covers all theorem declarations, rejects unexpected axiom dependencies, and writes verification.json with source hashes. It does not merely search for placeholder text: the Lean build is required to succeed.

The standard axiom dependencies allowed by the audit are propositional extensionality, classical choice, and quotient soundness. No use of sorryAx or custom mathematical axioms is accepted.

## Files

- FinGNO.lean imports every project module.
- FinGNO/ contains all definitions and proofs.
- Audit.lean prints the axiom dependencies of every theorem declaration.
- verify.py regenerates build.log, axioms.log, and verification.json.
- COVERAGE.md maps the formal declarations to manuscript results and states exclusions.
- lakefile.toml, lean-toolchain, and lake-manifest.json pin the project configuration.

Downloaded dependencies and generated binary caches are omitted from the source ZIP. Fetch the pinned dependencies before building on a new machine.

## Build-environment note

The environment used to prepare this package exposes its own executable path through /proc/self/exe, but does not expose that same path through /proc/<getpid()>/exe. Lean 4.19's executable discovery uses the latter spelling. The included optional tools/proc_self_compat.c changes only this self-identification request to the supported spelling. It makes no changes to Lean's proof kernel, imported mathematics, theorem statements, or proof terms.

This adapter is normally unnecessary on Linux, macOS, or Windows installations. In an environment with the same executable-discovery limitation, compile it with:

~~~bash
cc -shared -fPIC -O2 tools/proc_self_compat.c -ldl -o proc_self_compat.so
LD_PRELOAD="$PWD/proc_self_compat.so" python3 verify.py
~~~

The binary adapter is not distributed. The C source is included so the environment adjustment is inspectable. Set TAR_OPTIONS=--no-same-owner if a container cannot restore the original owner while extracting third-party cache tools. Neither adjustment changes mathematical checking.
