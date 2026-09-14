# Church scheduling playbook

## Outcome

Maintain a six-week published worship/ministry roster with named, qualified,
available people; recover from absence, overlapping services and shortages;
give members a schedule they can see and acknowledge.

Use Grace Community Church as a fictional sandbox. Run the shared commands in
[the acceptance guide](README.md). Executable headcounts live in [church.json](church.json).
Machine-readable actor and CH/BO traceability lives in [coverage.json](coverage.json);
its partial or blocked rows are remaining work, not passed scenarios.

## People and responsibilities

| Actor | Access | Responsibility |
| --- | --- | --- |
| Scheduling administrator | admin | Invite, record qualifications, create events, solve, review and publish |
| Worship coordinator | volunteer + worship_leader | Confirm service leadership; report absence |
| Musicians | volunteer + musician | Cover music and rehearsal assignments |
| Sound operators | volunteer + sound | Cover sound desk and technical rehearsal |
| Welcome team | volunteer + usher | Cover two distinct welcome positions |
| Children's ministry leaders | volunteer + children_leader | Confirm coverage and externally verified eligibility |
| Ministry approver | Human organizational responsibility | Approve suitability, safeguarding and service changes outside the solver |

Do not grant admin access merely because someone leads a ministry. The app has
only admin/volunteer access levels, not department-scoped manager permissions.

Prepare fourteen members: two worship leaders, four musicians, two sound
operators, four ushers and two children's leaders. Assign one qualification per
fixture person. A separate regression exercises a person qualified for two roles
and proves that they cannot fill both slots in the same event.

## Initial setup

1. Create the organization and administrator account. Check the onboarding page
   on a phone: the text and each action must remain readable and separate.
2. Invite all fourteen members with `volunteer` account access plus their scheduling
   qualification. Accept each invitation. Verify names and qualification strings in
   People before solving. The browser playbook executes this setup at 360px and 1440px.
3. Independently confirm each person's suitability for their ministry. A role
   label is not evidence of training, background screening or safeguarding approval.
4. Create six Sunday worship events, 10:00-12:00, one per week. Each needs one
   worship leader, two musicians, one sound operator, two ushers and one children's
   leader: seven distinct people, never six with one person counted twice.
5. Create Wednesday 18:00-20:00 ministry preparation/rehearsal sessions for the same
   six weeks and seven roles. Adapt actual ministry preparation duties to local practice.
6. Ask members to enter time off. Review eligibility and absence before generating
   the full six-week schedule in strict mode.

## Weekly operating rhythm

| When | Owner | Action and exit condition |
| --- | --- | --- |
| Monday | Administrator | Review upcoming six weeks, changes, staffing gaps and responses |
| Tuesday | Members | Record new absences and request replacements early |
| Wednesday | Ministry leads | Review preparation session attendance and next service needs |
| Thursday | Administrator | Regenerate remaining horizon; compare old and new rosters |
| Friday | Administrator + ministry approver | Resolve every gap, check each role, publish and communicate changes |
| Before service | Ministry leads | Confirm actual attendance and arrange qualified last-minute cover |
| After service | Administrator | Record follow-ups; review workload and prepare the next rolling week |

SignUpFlow schedules people. Attendance, ministry suitability, actual communication
and service execution remain human responsibilities, not inferred from a green solver score.

## Six-week exercise

| ID | Week / disruption | Actions | Acceptance |
| --- | --- | --- | --- |
| CH-01 | Baseline | Generate all twelve events and publish | Every event has seven qualified distinct assignees; interchangeable people's baseline loads differ by at most one |
| CH-02 | Leader away | Block one worship leader for Sunday week 2; regenerate | The absent leader has no assignment that date; reserve fills the leader slot |
| CH-03 | Extra service | Add week-3 service 11:00-13:00 | It overlaps 10:00-12:00; seven different people cover it; no person serves both |
| CH-04 | No leader available | Block both worship leaders for Sunday week 4 and attempt publication | Exactly that service reports missing worship leadership; publication is rejected and the prior roster stays live |
| CH-05 | New qualified cover | Invite and onboard a replacement worship leader | Regeneration fills week 4 and every other event; no other qualification is substituted |
| CH-06 | Service moved | Move week-6 Sunday event to Monday 10:00-12:00 | New solution carries the changed time and full coverage; publishing replaces the previous solution |
| CH-07 | Member acknowledgement | Open draft as assigned member, then publish and accept | Draft absent; published assignment is unanswered; explicit acceptance records the current revision in member and coordinator views |
| CH-08 | Qualified swap | Request a swap and have a reserve with the same qualification cover | Original member loses the shift; reserve gains it; every role remains filled |

CH-01 through CH-06 are one automated API lifecycle with assertions after each state
change. The browser journey creates all twelve CH-01 events through the multi-role form,
then independently verifies all 84 qualified, distinct, non-overlapping assignments and
balanced loads at phone and desktop sizes. CH-07/08 run in that same journey. BO-03
separately runs all five Church qualifications through one-off and recurring availability
entry at both widths, rejects peer edits, and verifies solver exclusion across twelve
API-seeded events.

BO-07 creates a weekly Church series in the browser, moves one service occurrence,
cancels a second, and proves the third is unchanged before deleting the remaining series.
The published-roster journey also proves that changing an accepted service time returns
the member commitment to unanswered until the member accepts the new revision.

BO-08 starts with a published Church fixture after both week-one sessions have completed.
At 360px and 1440px, the administrator adds the week-seven worship and rehearsal sessions,
solves and publishes weeks two through seven through the browser, and verifies all 84
qualified slots. The prior week remains visible as event history and every original future
service/rehearsal remains in the new horizon.

BO-09 runs a worship-leader account through the owned local mail backend at 360px and
1440px. The administrator creates the invitation, the member accepts its captured link,
requests a password reset, rejects the old password and replayed token, and signs in with
the replacement password. Publishing a service, moving its time, and sending a reminder
produce distinct durable messages plus matching member-inbox entries. The test opens the
captured schedule, availability, profile/calendar, and notification-preference links on
the same local server. Ministry approval and external inbox delivery remain human or
provider acceptance work.

BO-10 runs a qualified Church member's personal calendar at 360px and 1440px. A draft
service is absent; publication adds exactly one entry in `America/Toronto`; moving the
service updates the same UID and local time; cancelling it removes the entry on refresh.
The authenticated download and public token feed share the same published, non-declined,
tenant-scoped assignment policy. A separate unit case crosses the spring DST boundary.

BO-11 drives both the Church administrator and worship-leader member through logout/login,
self-service password change, and the actual link from locally captured reset email at both
browser widths. Their refreshed session stays usable, while copied pre-change/pre-reset
sessions, old passwords, replayed reset links, expired tokens, and short API reset passwords
fail without losing the account. Recovery screenshots are saved in pytest's temporary
directory; external mailbox delivery and distributed abuse controls remain separate work.

## Additional operational drills

Record these separately as manual/extended acceptance, not as passed by CH-01-08:

1. A sound operator requests a last-minute swap. Have a qualified, available reserve
   cover it; verify the original person loses the shift and the sound role remains filled.
2. A children's leader becomes ineligible. Remove that qualification, regenerate
   every affected future event, and obtain ministry approval before republishing.
3. A holiday changes service times or headcounts. Change only the intended events;
   verify recurrence exceptions and avoid changing already completed services.
4. A member never responds. Contact them through an approved channel and arrange
   confirmed cover; do not treat an assignment's default status as delivery evidence.
5. The venue is unavailable. Arrange a venue/time manually; the current playbook
   does not establish automated room conflict prevention.
6. Test a multi-skilled worship/sound member with another eligible specialist.
   Review any greedy-solver shortage manually; a feasible schedule is not guaranteed
   just because qualifications collectively appear sufficient.

## Release sign-off

Require exact role counts, no double-booking, no assignments during recorded
absence, no unpublished drafts exposed in member schedules, and successful member
acceptance. Recheck every future week after republishing. Keep human safeguarding,
external calendar-client polling, delivery, and broader tenant-security blockers visible
in the release record.
