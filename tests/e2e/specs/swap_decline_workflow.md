# Swap/Decline Workflow Spec

**User Goal**: As a volunteer, I want to decline an assignment or request a swap so that the event is covered.

## Workflows

### 1. Decline Assignment
1. Volunteer views "My Schedule".
2. Clicks on an assignment card.
3. Clicks "Decline / Swap".
4. Selects "I cannot serve" (Decline).
5. Enters reason (e.g., "Sick").
6. Confirms.
7. Assignment status changes to "declined".
8. Admin notified (mock).

### 2. Request Swap (Future)
1. Volunteer selects "Find Replacement".
2. System shows eligible volunteers.
3. Volunteer selects replacement.
4. Swap request sent.

## Technical Implementation

### Backend
- `PUT /api/assignments/{id}` - Update status (confirmed, declined, swap_requested)
- New fields on `Assignment` model: `status`, `decline_reason`

### Frontend
- Update `loadMySchedule` to show status badges (Declined vs Confirmed).
- Add `AssignmentDetailModal` with actions.
