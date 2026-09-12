import Mathlib.Tactic

namespace FinGNO

structure FiniteLaw (Ω : Type*) [Fintype Ω] where
  mass : Ω → ℝ
  nonneg : ∀ i, 0 ≤ mass i
  total : ∑ i, mass i = 1

variable {Ω : Type*} [Fintype Ω]

noncomputable def expectation (P : FiniteLaw Ω) (f : Ω → ℝ) : ℝ :=
  ∑ i, P.mass i * f i

noncomputable def totalVariation (P Q : FiniteLaw Ω) : ℝ :=
  (1/2) * ∑ i, |P.mass i - Q.mass i|

theorem tv_nonneg (P Q : FiniteLaw Ω) : 0 ≤ totalVariation P Q := by
  unfold totalVariation
  positivity

theorem tv_symm (P Q : FiniteLaw Ω) :
    totalVariation P Q = totalVariation Q P := by
  unfold totalVariation
  congr 1
  apply Finset.sum_congr rfl
  intro i _
  exact abs_sub_comm _ _

theorem tv_triangle (P Q R : FiniteLaw Ω) :
    totalVariation P R ≤ totalVariation P Q + totalVariation Q R := by
  have hpoint : ∀ i, |P.mass i - R.mass i| ≤
      |P.mass i - Q.mass i| + |Q.mass i - R.mass i| := by
    intro i
    have h : P.mass i - R.mass i =
        (P.mass i-Q.mass i)+(Q.mass i-R.mass i) := by ring
    rw [h]
    exact abs_add_le _ _
  have hs := Finset.sum_le_sum (fun i (_ : i ∈ Finset.univ) => hpoint i)
  rw [Finset.sum_add_distrib] at hs
  unfold totalVariation
  linarith

/-- Universal bounded-payoff inequality for actual finite probability laws.
The normalization of TV is one half of the L1 distance. -/
theorem bounded_expectation_error (P Q : FiniteLaw Ω)
    (C : Ω → ℝ) (B : ℝ)
    (hC : ∀ i, 0 ≤ C i ∧ C i ≤ B) :
    |expectation P C - expectation Q C| ≤ B * totalVariation P Q := by
  classical
  have hcenter : expectation P C - expectation Q C =
      ∑ i, (P.mass i-Q.mass i)*(C i-B/2) := by
    unfold expectation
    simp_rw [sub_mul, mul_sub]
    simp only [Finset.sum_sub_distrib, ← Finset.sum_mul]
    rw [P.total, Q.total]
    ring
  have hc : ∀ i, |C i-B/2| ≤ B/2 := by
    intro i
    rcases hC i with ⟨hlo, hhi⟩
    exact abs_le.mpr ⟨by linarith, by linarith⟩
  calc
    |expectation P C - expectation Q C| =
        |∑ i, (P.mass i-Q.mass i)*(C i-B/2)| := by rw [hcenter]
    _ ≤ ∑ i, |(P.mass i-Q.mass i)*(C i-B/2)| :=
      Finset.abs_sum_le_sum_abs _ _
    _ ≤ ∑ i, |P.mass i-Q.mass i| * (B/2) := by
      apply Finset.sum_le_sum
      intro i _
      rw [abs_mul]
      exact mul_le_mul_of_nonneg_left (hc i) (abs_nonneg _)
    _ = B * totalVariation P Q := by
      rw [← Finset.sum_mul]
      unfold totalVariation
      ring

theorem event_probability_error (P Q : FiniteLaw Ω) (A : Set Ω)
    [DecidablePred (fun i => i ∈ A)] :
    |expectation P (fun i => if i ∈ A then 1 else 0) -
     expectation Q (fun i => if i ∈ A then 1 else 0)| ≤ totalVariation P Q := by
  classical
  have h := bounded_expectation_error P Q
    (fun i => if i ∈ A then 1 else 0) 1
    (by intro i; by_cases hi : i ∈ A <;> simp [hi])
  simpa using h

end FinGNO
