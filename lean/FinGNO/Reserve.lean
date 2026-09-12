import Mathlib.Tactic

namespace FinGNO

structure Reserve where
  displayed : ℕ
  hidden : ℕ
deriving DecidableEq, Repr

structure Event where
  executed : ℕ
  replenished : ℕ
deriving DecidableEq, Repr

def applyEvent (s : Reserve) (e : Event) : Option Reserve :=
  if e.executed ≤ s.displayed ∧ e.replenished ≤ s.hidden then
    some ⟨s.displayed-e.executed+e.replenished, s.hidden-e.replenished⟩
  else none

theorem accepted_event_conserves (s out : Reserve) (e : Event)
    (h : applyEvent s e = some out) :
    out.displayed + out.hidden + e.executed = s.displayed + s.hidden := by
  unfold applyEvent at h
  split_ifs at h with hgood
  · rcases hgood with ⟨hq, hr⟩
    cases h
    simp only
    omega
def replay (s : Reserve) : List Event → Option Reserve
  | [] => some s
  | e::es => (applyEvent s e).bind (fun next => replay next es)

theorem accepted_replay_conserves (events : List Event) (s out : Reserve)
    (h : replay s events = some out) :
    out.displayed + out.hidden + (events.map Event.executed).sum =
      s.displayed + s.hidden := by
  induction events generalizing s with
  | nil =>
      simp only [replay, Option.some.injEq] at h
      subst s
      simp
  | cons e es ih =>
      cases he : applyEvent s e with
      | none => simp [replay, he] at h
      | some next =>
          have hr : replay next es = some out := by simpa [replay, he] using h
          have htail := ih next hr
          have hfirst := accepted_event_conserves s next e he
          simp only [List.map_cons, List.sum_cons]
          omega

end FinGNO
