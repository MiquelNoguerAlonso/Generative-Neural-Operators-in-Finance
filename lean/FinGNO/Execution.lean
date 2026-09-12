import FinGNO.FiniteLaws
import Mathlib.Tactic

namespace FinGNO

/-- Discrete quantile-prefix inequality. Interpreting sorted prices as optimal
one-dimensional transport remains a separate mathematical identification. -/
theorem prefix_cost_error (p q : ℕ → ℝ) (n N : ℕ) (hn : n ≤ N) :
    |(∑ i ∈ Finset.range n, p i) - (∑ i ∈ Finset.range n, q i)| ≤
      ∑ i ∈ Finset.range N, |p i-q i| := by
  rw [← Finset.sum_sub_distrib]
  calc
    |(∑ i ∈ Finset.range n, (p i - q i))| ≤
        ∑ i ∈ Finset.range n, |p i-q i| :=
      Finset.abs_sum_le_sum_abs _ _
    _ ≤ ∑ i ∈ Finset.range N, |p i-q i| := by
      apply Finset.sum_le_sum_of_subset_of_nonneg (Finset.range_mono hn)
      intro i _ _
      exact abs_nonneg _

/-- Policy comparison needs a uniform value error. The theorem quantifies over
every comparator and does not assume that a true optimizer exists. -/
theorem policy_regret {A : Type*} (J Jhat : A → ℝ)
    (chosen : A) (err eta : ℝ)
    (herror : ∀ a, |J a-Jhat a| ≤ err)
    (hchosen : ∀ a, Jhat chosen ≤ Jhat a+eta) :
    ∀ a, J chosen ≤ J a+2*err+eta := by
  intro a
  have h1 := (abs_le.mp (herror chosen)).2
  have h2 := (abs_le.mp (herror a)).1
  have h3 := hchosen a
  linarith

noncomputable def cvarObjective {Ω : Type*} [Fintype Ω]
    (P : FiniteLaw Ω) (C : Ω → ℝ) (alpha z : ℝ) : ℝ :=
  z + expectation P (fun i => max (C i-z) 0)/(1-alpha)

/-- The finite-law CVaR auxiliary objective bound, before taking the infimum
over z. The full real-infimum representation is proved in the paper. -/
theorem cvar_objective_error {Ω : Type*} [Fintype Ω]
    (P Q : FiniteLaw Ω) (C : Ω → ℝ) (B alpha z : ℝ)
    (hB : 0 ≤ B) (ha : alpha < 1) (hz : 0 ≤ z)
    (hC : ∀ i, 0 ≤ C i ∧ C i ≤ B) :
    |cvarObjective P C alpha z - cvarObjective Q C alpha z| ≤
      B*totalVariation P Q/(1-alpha) := by
  have hpay : ∀ i, 0 ≤ max (C i-z) 0 ∧ max (C i-z) 0 ≤ B := by
    intro i
    constructor
    · exact le_max_right _ _
    · apply max_le
      · linarith [(hC i).2]
      · exact hB
  have he := bounded_expectation_error P Q (fun i => max (C i-z) 0) B hpay
  have hd : 0 < 1-alpha := by linarith
  unfold cvarObjective
  have hid : z + expectation P (fun i => max (C i-z) 0)/(1-alpha) -
      (z + expectation Q (fun i => max (C i-z) 0)/(1-alpha)) =
      (expectation P (fun i => max (C i-z) 0) -
       expectation Q (fun i => max (C i-z) 0))/(1-alpha) := by ring
  rw [hid, abs_div, abs_of_pos hd]
  exact div_le_div_of_nonneg_right he (le_of_lt hd)

end FinGNO
