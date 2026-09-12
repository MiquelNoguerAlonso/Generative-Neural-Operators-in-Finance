import Mathlib.Analysis.SpecialFunctions.Sqrt
import Mathlib.Analysis.SpecialFunctions.Exp
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Tactic

/-!
# The algebraic core of the orthogonal refinement certificate

radius eps L n is the paper's d_(n-1): n counts completed bands.
The probabilistic coupling argument supplying hstep in
error_le_radius is NOT assumed to have been formalized by this module.
All results below are theorems about real numbers, not floating-point tests.
-/

namespace FinGNO

noncomputable def radius (eps L : ℕ → ℝ) : ℕ → ℝ
  | 0 => 0
  | n + 1 => Real.sqrt ((radius eps L n)^2 +
      (eps n + L n * radius eps L n)^2)

theorem radius_nonneg (eps L : ℕ → ℝ) (n : ℕ) :
    0 ≤ radius eps L n := by
  cases n with
  | zero => simp [radius]
  | succ n => exact Real.sqrt_nonneg _

theorem radius_sq_succ (eps L : ℕ → ℝ) (n : ℕ) :
    (radius eps L (n+1))^2 =
      (radius eps L n)^2 + (eps n + L n * radius eps L n)^2 := by
  simp only [radius]
  exact Real.sq_sqrt (add_nonneg (sq_nonneg _) (sq_nonneg _))

theorem radius_monotone (eps L : ℕ → ℝ) :
    Monotone (radius eps L) := by
  apply monotone_nat_of_le_succ
  intro n
  have hn := radius_nonneg eps L n
  have hs := radius_nonneg eps L (n+1)
  have he := radius_sq_succ eps L n
  nlinarith [sq_nonneg (eps n + L n * radius eps L n)]

theorem square_step_monotone {eps L x y : ℝ}
    (he : 0 ≤ eps) (hL : 0 ≤ L) (hx : 0 ≤ x) (hxy : x ≤ y) :
    x^2 + (eps + L*x)^2 ≤ y^2 + (eps + L*y)^2 := by
  have hy : 0 ≤ y := le_trans hx hxy
  have hmul : L*x ≤ L*y := mul_le_mul_of_nonneg_left hxy hL
  have ha : 0 ≤ eps + L*x := add_nonneg he (mul_nonneg hL hx)
  have hb : 0 ≤ eps + L*y := add_nonneg he (mul_nonneg hL hy)
  nlinarith [sq_nonneg (y-x), sq_nonneg ((eps+L*y)-(eps+L*x))]

theorem error_le_radius (eps L D : ℕ → ℝ)
    (he : ∀ n, 0 ≤ eps n) (hL : ∀ n, 0 ≤ L n)
    (hD : ∀ n, 0 ≤ D n) (hzero : D 0 = 0)
    (hstep : ∀ n, (D (n+1))^2 ≤
      (D n)^2 + (eps n + L n * D n)^2) :
    ∀ n, D n ≤ radius eps L n := by
  intro n
  induction n with
  | zero => simp [hzero, radius]
  | succ n ih =>
      have hm := square_step_monotone (he n) (hL n) (hD n) ih
      have hs := radius_sq_succ eps L n
      have hr := radius_nonneg eps L (n+1)
      have hd := hD (n+1)
      have hb := hstep n
      nlinarith

theorem radius_step_bound (eps L : ℕ → ℝ) (n : ℕ) :
    (radius eps L (n+1))^2 ≤
      (1 + 2*(L n)^2) * (radius eps L n)^2 + 2*(eps n)^2 := by
  rw [radius_sq_succ]
  nlinarith [sq_nonneg (eps n - L n * radius eps L n)]

noncomputable def linearBound (eps L : ℕ → ℝ) : ℕ → ℝ
  | 0 => 0
  | n+1 => (1 + 2*(L n)^2) * linearBound eps L n + 2*(eps n)^2

theorem radius_sq_le_linearBound (eps L : ℕ → ℝ) (n : ℕ) :
    (radius eps L n)^2 ≤ linearBound eps L n := by
  induction n with
  | zero => simp [radius, linearBound]
  | succ n ih =>
      have hc : 0 ≤ 1 + 2*(L n)^2 := by positivity
      have hm := mul_le_mul_of_nonneg_left ih hc
      have hs := radius_step_bound eps L n
      simp only [linearBound]
      linarith

theorem context_independent_exact (eps : ℕ → ℝ) (n : ℕ) :
    (radius eps (fun _ => 0) n)^2 =
      ∑ j ∈ Finset.range n, (eps j)^2 := by
  induction n with
  | zero => simp [radius]
  | succ n ih =>
      rw [radius_sq_succ, Finset.sum_range_succ, ih]
      simp

theorem exponential_certificate (eps L : ℕ → ℝ) (n : ℕ) :
    (radius eps L n)^2 ≤
      2 * Real.exp (2 * ∑ j ∈ Finset.range n, (L j)^2) *
      (∑ j ∈ Finset.range n, (eps j)^2) := by
  induction n with
  | zero => simp [radius]
  | succ n ih =>
      let S : ℝ := ∑ j ∈ Finset.range n, (L j)^2
      let E : ℝ := ∑ j ∈ Finset.range n, (eps j)^2
      have hS : 0 ≤ S := Finset.sum_nonneg (fun i _ => sq_nonneg (L i))
      have hE : 0 ≤ E := Finset.sum_nonneg (fun i _ => sq_nonneg (eps i))
      have heS : 1 ≤ Real.exp (2*S) := Real.one_le_exp (by positivity)
      have heL : 1 ≤ Real.exp (2*(L n)^2) := Real.one_le_exp (by positivity)
      have hlin : 1 + 2*(L n)^2 ≤ Real.exp (2*(L n)^2) := by
        linarith [Real.add_one_le_exp (2*(L n)^2)]
      have hc : 0 ≤ 1 + 2*(L n)^2 := by positivity
      have hbase : (radius eps L n)^2 ≤ 2 * Real.exp (2*S) * E := ih
      have hmul := mul_le_mul_of_nonneg_left hbase hc
      have hmul2 := mul_le_mul_of_nonneg_right hlin
        (show 0 ≤ 2 * Real.exp (2*S) * E by positivity)
      have hexp : Real.exp (2*(S+(L n)^2)) =
          Real.exp (2*S) * Real.exp (2*(L n)^2) := by
        rw [mul_add, Real.exp_add]
      have hprod : 1 ≤ Real.exp (2*S) * Real.exp (2*(L n)^2) := by
        nlinarith
      have heps := mul_le_mul_of_nonneg_right hprod
        (show 0 ≤ 2*(eps n)^2 by positivity)
      have hstep := radius_step_bound eps L n
      simp only [Finset.sum_range_succ]
      change (radius eps L (n+1))^2 ≤
        2 * Real.exp (2*(S+(L n)^2)) * (E+(eps n)^2)
      rw [hexp]
      nlinarith

/-- Given the orthogonal decomposition, propagate the projected certificate.
No Wasserstein objects are defined here. -/
theorem add_tail_certificate {full projected tail bound : ℝ}
    (hdecomp : full^2 = tail^2 + projected^2)
    (hprojected : projected^2 ≤ bound^2) :
    full^2 ≤ tail^2 + bound^2 := by
  linarith

end FinGNO
