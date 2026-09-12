import FinGNO.FiniteLaws
import Mathlib.Tactic

namespace FinGNO

variable {Ω E : Type*} [Fintype Ω] [Fintype E]

noncomputable def jointLaw (P : FiniteLaw Ω) (K : Ω → FiniteLaw E) :
    FiniteLaw (Ω × E) where
  mass := fun z => P.mass z.1 * (K z.1).mass z.2
  nonneg := fun z => mul_nonneg (P.nonneg z.1) ((K z.1).nonneg z.2)
  total := by
    rw [Fintype.sum_prod_type]
    simp_rw [← Finset.mul_sum, FiniteLaw.total, mul_one]
    exact P.total

theorem joint_tv_same_base (P : FiniteLaw Ω) (K L : Ω → FiniteLaw E) :
    totalVariation (jointLaw P K) (jointLaw P L) =
      ∑ x, P.mass x * totalVariation (K x) (L x) := by
  unfold totalVariation jointLaw
  simp only
  rw [Fintype.sum_prod_type]
  simp_rw [← mul_sub, abs_mul, abs_of_nonneg (P.nonneg _), ← Finset.mul_sum]
  rw [Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro x _
  ring

theorem joint_tv_same_kernel (P Q : FiniteLaw Ω) (K : Ω → FiniteLaw E) :
    totalVariation (jointLaw P K) (jointLaw Q K) = totalVariation P Q := by
  unfold totalVariation jointLaw
  simp only
  rw [Fintype.sum_prod_type]
  simp_rw [← sub_mul, abs_mul, abs_of_nonneg ((K _).nonneg _),
    ← Finset.mul_sum, FiniteLaw.total, mul_one]

theorem joint_tv_bound (P Q : FiniteLaw Ω) (K L : Ω → FiniteLaw E) :
    totalVariation (jointLaw P K) (jointLaw Q L) ≤
      totalVariation P Q + ∑ x, P.mass x * totalVariation (K x) (L x) := by
  have h := tv_triangle (jointLaw P K) (jointLaw P L) (jointLaw Q L)
  rw [joint_tv_same_base, joint_tv_same_kernel] at h
  linarith

theorem joint_tv_uniform (P Q : FiniteLaw Ω) (K L : Ω → FiniteLaw E)
    {eps : ℝ} (h : ∀ x, totalVariation (K x) (L x) ≤ eps) :
    totalVariation (jointLaw P K) (jointLaw Q L) ≤ totalVariation P Q + eps := by
  have hh : (∑ x, P.mass x * totalVariation (K x) (L x)) ≤ eps := by
    calc
      _ ≤ ∑ x, P.mass x * eps := by
        apply Finset.sum_le_sum
        intro x _
        exact mul_le_mul_of_nonneg_left (h x) (P.nonneg x)
      _ = eps := by rw [← Finset.sum_mul, P.total, one_mul]
  exact (joint_tv_bound P Q K L).trans (add_le_add_left hh _)

universe v
/-- Histories retain every mark, so their TV is path-law TV, not terminal-state TV. -/
def History (E : Type v) : ℕ → Type v
  | 0 => PUnit
  | n+1 => History E n × E

instance historyFintype (E : Type*) [Fintype E] (n : ℕ) : Fintype (History E n) := by
  induction n with
  | zero => exact inferInstanceAs (Fintype PUnit)
  | succ n ih =>
      letI : Fintype (History E n) := ih
      exact inferInstanceAs (Fintype (History E n × E))

noncomputable def historyLaw (K : ∀ n, History E n → FiniteLaw E) :
    (n : ℕ) → FiniteLaw (History E n)
  | 0 => {mass := fun _ => 1, nonneg := by intro _; norm_num,
          total := by simp [History, historyFintype]}
  | n+1 => jointLaw (historyLaw K n) (K n)

theorem history_tv_bound (K L : ∀ n, History E n → FiniteLaw E)
    (eps : ℕ → ℝ)
    (h : ∀ n x, totalVariation (K n x) (L n x) ≤ eps n) (n : ℕ) :
    totalVariation (historyLaw K n) (historyLaw L n) ≤
      ∑ k ∈ Finset.range n, eps k := by
  induction n with
  | zero => simp [historyLaw, totalVariation]
  | succ n ih =>
      change totalVariation (jointLaw (historyLaw K n) (K n))
        (jointLaw (historyLaw L n) (L n)) ≤ _
      have hs := joint_tv_uniform (historyLaw K n) (historyLaw L n) (K n) (L n) (h n)
      rw [Finset.sum_range_succ]
      linarith

/-- Finite posterior randomization has the intended acceptance probability. -/
theorem posterior_acceptance_probability (P : FiniteLaw Ω) (rate : Ω → ℝ)
    {c : ℝ} (hc : 0 < c) (hr : ∀ x, 0 ≤ rate x ∧ rate x ≤ c) :
    0 ≤ ∑ x, P.mass x * (rate x/c) ∧
      (∑ x, P.mass x * (rate x/c)) ≤ 1 := by
  constructor
  · apply Finset.sum_nonneg
    intro x _
    exact mul_nonneg (P.nonneg x) (div_nonneg (hr x).1 hc.le)
  · calc
      _ ≤ ∑ x, P.mass x * 1 := by
        apply Finset.sum_le_sum
        intro x _
        exact mul_le_mul_of_nonneg_left ((div_le_one hc).2 (hr x).2) (P.nonneg x)
      _ = 1 := by simpa using P.total

theorem posterior_thinning_rate (P : FiniteLaw Ω) (rate : Ω → ℝ)
    {c : ℝ} (hc : c ≠ 0) :
    c * (∑ x, P.mass x * (rate x/c)) = expectation P rate := by
  unfold expectation
  rw [Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro x _
  field_simp

end FinGNO
