import FinGNO.FiniteLaws
import Mathlib.Tactic

namespace FinGNO

variable {Ω : Type*} [Fintype Ω]

theorem positive_expectation (P : FiniteLaw Ω) (g : Ω → ℝ)
    (hg : ∀ i, 0 < g i) : 0 < expectation P g := by
  classical
  have hex : ∃ i, 0 < P.mass i := by
    by_contra! h
    have hs : (∑ i, P.mass i) ≤ 0 :=
      Finset.sum_nonpos (fun i _ => h i)
    rw [P.total] at hs
    norm_num at hs
  obtain ⟨i, hi⟩ := hex
  unfold expectation
  exact Finset.sum_pos'
    (fun j _ => mul_nonneg (P.nonneg j) (le_of_lt (hg j)))
    ⟨i, Finset.mem_univ i, mul_pos hi (hg i)⟩

noncomputable def normalizedReturn (P : FiniteLaw Ω) (g : Ω → ℝ)
    (i : Ω) : ℝ := g i / expectation P g

theorem normalized_return_positive (P : FiniteLaw Ω) (g : Ω → ℝ)
    (hg : ∀ i, 0 < g i) (i : Ω) :
    0 < normalizedReturn P g i := by
  exact div_pos (hg i) (positive_expectation P g hg)

theorem normalized_return_mean_one (P : FiniteLaw Ω) (g : Ω → ℝ)
    (hg : ∀ i, 0 < g i) :
    expectation P (normalizedReturn P g) = 1 := by
  have hm : expectation P g ≠ 0 := ne_of_gt (positive_expectation P g hg)
  change (∑ i, P.mass i*(g i/expectation P g)) = 1
  simp_rw [← mul_div_assoc]
  rw [← Finset.sum_div]
  change expectation P g / expectation P g = 1
  exact div_self hm

theorem normalized_step_mean (P : FiniteLaw Ω) (g : Ω → ℝ)
    (hg : ∀ i, 0 < g i) (x : ℝ) :
    expectation P (fun i => x*normalizedReturn P g i) = x := by
  have hm := normalized_return_mean_one P g hg
  unfold expectation at hm ⊢
  calc
    (∑ i, P.mass i*(x*normalizedReturn P g i)) =
        x*(∑ i, P.mass i*normalizedReturn P g i) := by
      rw [Finset.mul_sum]
      apply Finset.sum_congr rfl
      intro i _
      ring
    _ = x := by rw [hm]; ring

end FinGNO
