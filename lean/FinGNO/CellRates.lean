import Mathlib.Analysis.SpecialFunctions.Sqrt
import Mathlib.Tactic

namespace FinGNO

/-- Finite quadrature analogue of cell integration's L1 contraction. -/
theorem cell_integration_contraction {C I : Type*} [Fintype C] [Fintype I]
    (w f g : C → I → ℝ) (hw : ∀ c i, 0 ≤ w c i) :
    (∑ c, |∑ i, w c i*(f c i-g c i)|) ≤
      ∑ c, ∑ i, w c i*|f c i-g c i| := by
  apply Finset.sum_le_sum
  intro c _
  calc
    |∑ i, w c i*(f c i-g c i)| ≤ ∑ i, |w c i*(f c i-g c i)| :=
      Finset.abs_sum_le_sum_abs _ _
    _ = ∑ i, w c i*|f c i-g c i| := by
      apply Finset.sum_congr rfl
      intro i _
      rw [abs_mul, abs_of_nonneg (hw c i)]

/-- Weighted finite Cauchy-Schwarz with the mass constant of the chosen
quadrature measure, rather than the number of coordinates. -/
theorem weighted_l1_square_bound {I : Type*} [Fintype I]
    (w d : I → ℝ) (hw : ∀ i, 0 ≤ w i) :
    (∑ i, w i * |d i|)^2 ≤ (∑ i, w i) * (∑ i, w i * (d i)^2) := by
  apply Finset.sum_sq_le_sum_mul_sum_of_sq_eq_mul Finset.univ
    (fun i _ => hw i) (fun i _ => mul_nonneg (hw i) (sq_nonneg _))
  intro i _
  rw [mul_pow, sq_abs]
  ring

theorem weighted_l1_l2_bound {I : Type*} [Fintype I]
    (w d : I → ℝ) (hw : ∀ i, 0 ≤ w i) :
    (∑ i, w i * |d i|) ≤
      Real.sqrt (∑ i, w i) * Real.sqrt (∑ i, w i * (d i)^2) := by
  have hM : 0 ≤ ∑ i, w i := Finset.sum_nonneg (fun i _ => hw i)
  have hE : 0 ≤ ∑ i, w i*(d i)^2 :=
    Finset.sum_nonneg (fun i _ => mul_nonneg (hw i) (sq_nonneg _))
  have hA : 0 ≤ ∑ i, w i * |d i| :=
    Finset.sum_nonneg (fun i _ => mul_nonneg (hw i) (abs_nonneg _))
  have hR : 0 ≤ Real.sqrt (∑ i, w i) *
      Real.sqrt (∑ i, w i*(d i)^2) := by positivity
  have hRsq : (Real.sqrt (∑ i, w i) *
      Real.sqrt (∑ i, w i*(d i)^2))^2 =
      (∑ i, w i)*(∑ i, w i*(d i)^2) := by
    rw [mul_pow, Real.sq_sqrt hM, Real.sq_sqrt hE]
  have hc := weighted_l1_square_bound w d hw
  nlinarith

end FinGNO
