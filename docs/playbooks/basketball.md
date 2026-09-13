# Basketball scheduling playbook

## Outcome

Maintain a six-week basketball game and practice roster with five distinct player
positions, coaching and scorekeeping coverage, available reserves and a reliable
publish/respond workflow. This is roster scheduling, not live game management.

Use Riverside Basketball as a fictional single-team sandbox. See
[the acceptance guide](README.md) and executable [basketball.json](basketball.json).
Machine-readable actor and BB/BO traceability lives in [coverage.json](coverage.json);
its partial or blocked rows are remaining work, not passed scenarios.

## People and responsibilities

| Actor | Access | Responsibility |
| --- | --- | --- |
| Team manager | admin | Invite members, create sessions, review coverage, publish changes |
| Coaches | volunteer + coach | Confirm availability and operational readiness |
| Point guards | volunteer + point_guard | Cover one point-guard slot per event |
| Shooting guards | volunteer + shooting_guard | Cover one shooting-guard slot |
| Small forwards | volunteer + small_forward | Cover one small-forward slot |
| Power forwards | volunteer + power_forward | Cover one power-forward slot |
| Centers | volunteer + center | Cover one center slot |
| Scorekeepers | volunteer + scorekeeper | Cover game table and practice/statistics duties |

Prepare two people per role: ten players, two coaches and two scorekeepers.
Use `volunteer` plus the listed scheduling role; coaching must not implicitly
grant administrator access. Qualifications in this exercise describe the intended
lineup, not league registration, age eligibility or medical clearance.

## Initial setup

1. Create the team organization and manager account. Invite fourteen people and
   accept the invitations. Verify each scheduling qualification explicitly.
2. Arrange venues and opponent/game details outside the solver. Use event titles
   and organizational records consistently; the fixture has no opponent or league engine.
3. Create six Sunday games, 10:00-12:00, with one of each player position, one
   coach and one scorekeeper: seven distinct assignments per event.
4. Create six Wednesday practices, 18:00-20:00, using the same role requirements
   for this exercise. In a real team, adjust practice headcounts to the session plan.
5. Ask members to record absences. Generate the full horizon and review the named
   lineup rather than relying on the overall health score.
6. Publish only after resolving gaps. Have members open their own schedules and
   acknowledge the assignment. Keep reserves and communication arrangements explicit.

## Weekly operating rhythm

| When | Owner | Action and exit condition |
| --- | --- | --- |
| Monday | Manager | Review six-week game/practice calendar, venue changes and responses |
| Tuesday | Players and staff | Record availability and known travel/injury absences |
| Wednesday | Coach | Run practice; identify personnel changes for the upcoming game |
| Thursday | Manager | Regenerate, check positions and staff, compare changes |
| Friday | Coach + manager | Confirm lineup and reserves, publish and communicate |
| Game day | Coach + scorekeeper | Verify actual attendance and handle in-game duties outside SignUpFlow |
| After game | Manager | Review schedule workload and prepare the next rolling week |

Equal assignment counts are not equal playing minutes. The application does not
choose tactical substitutions or enforce league participation rules.

## Six-week exercise

| ID | Week / disruption | Actions | Acceptance |
| --- | --- | --- | --- |
| BB-01 | Baseline | Generate twelve events and publish | Five distinct positions plus coach and scorekeeper on every event; interchangeable baseline loads differ by at most one |
| BB-02 | Player absent | Block one point guard for Sunday week 2 | That player is excluded that date; the other qualified point guard covers |
| BB-03 | Overlapping game | Add week-3 game 11:00-13:00 | Disjoint players and staff cover both simultaneous games; no double-booking |
| BB-04 | Position unavailable | Block both point guards for Sunday week 4 | That game has a reported point-guard shortage; failing draft is not published |
| BB-05 | Replacement onboarded | Invite another qualified point guard | Regeneration repairs the gap without assigning a center or coach to that position |
| BB-06 | Game postponed | Move week-6 game to Monday 10:00-12:00 | Regenerated schedule contains the new time with all roles covered; publication replaces the old version |
| BB-07 | Player acknowledgement | View draft as player, publish, then accept | Draft is invisible to player; published assignment appears and can be accepted in browser |
| BB-08 | Qualified swap | Request a swap and have a reserve for the same position cover | Original player loses the shift; reserve gains it; all position/staff slots remain covered |

BB-01 through BB-06 run as an automated API lifecycle. BB-07/08 and multi-role form
entry run in Chromium at phone and desktop sizes. The overlapping-game scenario
is a staffing capacity drill, not a recommendation to split a competition team.

## Additional operational drills

Record these separately as manual/extended acceptance:

1. A player requests a swap. Use a reserve qualified for the same position; verify
   the roster has exactly one person in that slot and the original player loses it.
2. A coach or scorekeeper withdraws on game day. Arrange qualified cover and verify
   it is visible to both the replacement and manager before relying on it.
3. A venue cancels a game. Coordinate the postponement, inspect calendar exports,
   communicate the change and obtain responses. Automated court collision and
   notification delivery are not established by this exercise.
4. Two teams share players in one organization. Test team eligibility explicitly
   before use; current role-based solving is not proven to restrict by team roster.
5. A tournament needs travel/rest gaps. Validate manually; API solver integration
   currently ignores saved custom constraints, so a configured gap is not proof.
6. An injury affects several weeks. Record the correct date range, regenerate
   the entire future horizon and follow the organization's separate return policy.
7. A member needs calendar export or uses a different timezone. Check actual dates
   and device rendering; these domain tests use UTC and do not certify DST behavior.

## Release sign-off

Require complete position/staff coverage, distinct people at overlapping times,
absence compliance, visible published schedules and successful member acceptance.
Keep game execution, playing time, league eligibility, delivery and security
blockers separate from the scheduling acceptance result.
