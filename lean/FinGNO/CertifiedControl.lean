import FinGNO.FiniteLaws
import Mathlib.Tactic

namespace FinGNO

theorem rate_box_endpoints (lo hi q gamma : ℝ) (hl : lo ≤ q) (hu : q ≤ hi) :
    (if 0 ≤ gamma then lo*gamma else hi*gamma) ≤ q*gamma ∧
    q*gamma ≤ (if 0 ≤ gamma then hi*gamma else lo*gamma) := by
  by_cases hg : 0 ≤ gamma
  · simp only [if_pos hg]
    exact ⟨mul_le_mul_of_nonneg_right hl hg, mul_le_mul_of_nonneg_right hu hg⟩
  · simp only [if_neg hg]
    have hn : gamma ≤ 0 := le_of_lt (lt_of_not_ge hg)
    exact ⟨mul_le_mul_of_nonpos_right hu hn, mul_le_mul_of_nonpos_right hl hn⟩

/-- Policy-specific uncertainty cancels for the chosen policy, leaving twice
the comparator's radius. The confidence event itself is supplied separately. -/
theorem pessimistic_policy_regret {A : Type*} (J Jhat r : A → ℝ)
    (chosen : A) (eta : ℝ)
    (herror : ∀ a, |J a-Jhat a| ≤ r a)
    (hchosen : ∀ a, Jhat chosen+r chosen ≤ Jhat a+r a+eta) :
    ∀ a, J chosen ≤ J a+2*r a+eta := by
  intro a
  have hc := (abs_le.mp (herror chosen)).2
  have ha := (abs_le.mp (herror a)).1
  have hs := hchosen a
  linarith

variable {X A : Type*} [Fintype X]

theorem expectation_monotone (P : FiniteLaw X) (f g : X → ℝ)
    (h : ∀ x, f x ≤ g x) : expectation P f ≤ expectation P g := by
  exact Finset.sum_le_sum (fun x _ => mul_le_mul_of_nonneg_left (h x) (P.nonneg x))

theorem expectation_sup_error (P : FiniteLaw X) (f g : X → ℝ) (b : ℝ)
    (h : ∀ x, |f x-g x| ≤ b) : |expectation P f-expectation P g| ≤ b := by
  calc
    _ = |∑ x, P.mass x*(f x-g x)| := by simp [expectation, mul_sub, Finset.sum_sub_distrib]
    _ ≤ ∑ x, |P.mass x*(f x-g x)| := Finset.abs_sum_le_sum_abs _ _
    _ ≤ ∑ x, P.mass x*b := by
      apply Finset.sum_le_sum
      intro x _
      rw [abs_mul, abs_of_nonneg (P.nonneg x)]
      exact mul_le_mul_of_nonneg_left (h x) (P.nonneg x)
    _ = b := by rw [← Finset.sum_mul, P.total, one_mul]

/-- Actual finite-horizon evaluation under a finite stochastic transition law.
The time index denotes the number of decisions remaining. -/
noncomputable def policyValue (K : X → A → FiniteLaw X)
    (cost : X → A → ℝ) (terminal : X → ℝ) (policy : ℕ → X → A) : ℕ → X → ℝ
  | 0, x => terminal x
  | n+1, x => cost x (policy n x) + expectation (K x (policy n x))
      (policyValue K cost terminal policy n)

/-- A finite probabilistic robust sandwich. Subsolution inequalities hold for
all actions; the supersolution inequality only needs the deployed action.
This does not assert a formalization of continuous-time Dynkin's identity. -/
theorem finite_robust_sandwich (K : X → A → FiniteLaw X)
    (cost : X → A → ℝ) (terminal : X → ℝ) (chosen : ℕ → X → A)
    (L U : ℕ → X → ℝ)
    (hl0 : ∀ x, L 0 x ≤ terminal x) (hu0 : ∀ x, terminal x ≤ U 0 x)
    (hl : ∀ n x a, L (n+1) x ≤ cost x a + expectation (K x a) (L n))
    (hu : ∀ n x, cost x (chosen n x)+expectation (K x (chosen n x)) (U n) ≤ U (n+1) x) :
    (∀ policy n x, L n x ≤ policyValue K cost terminal policy n x) ∧
    (∀ n x, policyValue K cost terminal chosen n x ≤ U n x) := by
  constructor
  · intro policy n
    induction n with
    | zero => exact hl0
    | succ n ih =>
        intro x
        exact le_trans (hl n x (policy n x))
          (add_le_add_left (expectation_monotone (K x (policy n x)) _ _ ih) _)
  · intro n
    induction n with
    | zero => exact hu0
    | succ n ih =>
        intro x
        exact le_trans
          (add_le_add_left (expectation_monotone (K x (chosen n x)) _ _ ih) _)
          (hu n x)

/-- Local Bellman residuals add, without an exponential factor, under actual
normalized nonnegative transition laws. This is the finite-step counterpart
of the manuscript's continuous-time comparison argument. -/
theorem finite_horizon_residual (K : X → A → FiniteLaw X)
    (cost : X → A → ℝ) (terminal : X → ℝ) (policy : ℕ → X → A)
    (v : ℕ → X → ℝ) (r : ℕ → ℝ)
    (hzero : ∀ x, v 0 x = terminal x)
    (hstep : ∀ n x, |v (n+1) x -
      (cost x (policy n x)+expectation (K x (policy n x)) (v n))| ≤ r n) :
    ∀ n x, |v n x-policyValue K cost terminal policy n x| ≤
      ∑ j ∈ Finset.range n, r j := by
  intro n
  induction n with
  | zero => intro x; simp [policyValue, hzero]
  | succ n ih =>
      intro x
      have he := expectation_sup_error (K x (policy n x)) (v n)
        (policyValue K cost terminal policy n) (∑ j ∈ Finset.range n, r j) ih
      have ht := abs_add_le
        (v (n+1) x-(cost x (policy n x)+expectation (K x (policy n x)) (v n)))
        (expectation (K x (policy n x)) (v n)-
          expectation (K x (policy n x)) (policyValue K cost terminal policy n))
      have hid : v (n+1) x-(cost x (policy n x)+expectation (K x (policy n x)) (v n)) +
          (expectation (K x (policy n x)) (v n)-
            expectation (K x (policy n x)) (policyValue K cost terminal policy n)) =
          v (n+1) x-policyValue K cost terminal policy (n+1) x := by
        simp only [policyValue]; ring
      rw [hid] at ht
      rw [Finset.sum_range_succ]
      linarith [hstep n x]

end FinGNO
