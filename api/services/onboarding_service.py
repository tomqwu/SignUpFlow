"""
Onboarding Service

Business logic for managing user onboarding progress, wizard states,
and checklist evaluations.
"""

import logging
from typing import Optional, Dict, List, Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from api.models import OnboardingProgress, Person, Organization, Event, Team, Assignment, Invitation

logger = logging.getLogger(__name__)

class OnboardingService:
    """
    Service for managing onboarding workflows.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_progress(self, person_id: str) -> OnboardingProgress:
        """
        Get or create onboarding progress for a user.
        """
        progress = self.db.query(OnboardingProgress).filter(
            OnboardingProgress.person_id == person_id
        ).first()

        if not progress:
            # Need org_id to create progress
            person = self.db.query(Person).filter(Person.id == person_id).first()
            if not person:
                raise ValueError(f"Person not found: {person_id}")

            progress = OnboardingProgress(
                person_id=person_id,
                org_id=person.org_id,
                wizard_step_completed=0,
                wizard_data={},
                checklist_state={},
                tutorials_completed=[],
                features_unlocked=[],
                videos_watched=[],
                onboarding_skipped=False
            )
            self.db.add(progress)
            try:
                self.db.commit()
            except IntegrityError:
                # If multiple concurrent requests try to create progress for the same
                # person, the UNIQUE(person_id) constraint can race. Make this
                # operation idempotent by rolling back and loading the existing row.
                self.db.rollback()
                progress = self.db.query(OnboardingProgress).filter(
                    OnboardingProgress.person_id == person_id
                ).first()
                if not progress:
                    raise
            else:
                self.db.refresh(progress)

        # Evaluate checklist tasks dynamically if needed
        self._evaluate_checklist(progress)
        
        return progress

    def update_progress(self, person_id: str, data: Dict[str, Any]) -> OnboardingProgress:
        """
        Update onboarding progress fields.
        """
        progress = self.get_progress(person_id)

        # List of updatable fields
        fields = [
            "wizard_step_completed",
            "wizard_data",
            "checklist_state",
            "tutorials_completed",
            "features_unlocked",
            "videos_watched",
            "onboarding_skipped",
            "checklist_dismissed",
            "tutorials_dismissed"
        ]

        for field in fields:
            if field in data and data[field] is not None:
                if field == "checklist_state" and progress.checklist_state:
                    # Merge checklist state
                    current = dict(progress.checklist_state)
                    current.update(data[field])
                    progress.checklist_state = current
                    flag_modified(progress, "checklist_state")
                else:
                    setattr(progress, field, data[field])
                    if isinstance(data[field], (dict, list)):
                        flag_modified(progress, field)

        self.db.commit()
        self.db.refresh(progress)
        return progress

    def skip_onboarding(self, person_id: str) -> bool:
        """
        Mark onboarding as skipped.
        """
        self.update_progress(person_id, {
            "wizard_step_completed": 4,
            "onboarding_skipped": True
        })
        return True

    def reset_onboarding(self, person_id: str) -> bool:
        """
        Reset onboarding progress.
        """
        progress = self.get_progress(person_id)
        progress.wizard_step_completed = 0
        progress.wizard_data = {}
        progress.checklist_state = {}
        progress.tutorials_completed = []
        progress.features_unlocked = []
        progress.onboarding_skipped = False
        
        self.db.commit()
        return True

    def _evaluate_checklist(self, progress: OnboardingProgress):
        """
        Evaluate checklist tasks based on actual database state.
        """
        org_id = progress.org_id
        person_id = progress.person_id
        
        state = dict(progress.checklist_state or {})
        
        # 1. Complete Profile (checked if user has a name and timezone)
        person = self.db.query(Person).filter(Person.id == person_id).first()
        if person and person.name and person.timezone != "UTC":
            state["complete_profile"] = True

        # 2. Create First Event
        event_count = self.db.query(Event).filter(Event.org_id == org_id).count()
        if event_count > 0:
            state["create_event"] = True

        # 3. Add Team
        team_count = self.db.query(Team).filter(Team.org_id == org_id).count()
        if team_count > 0:
            state["add_team"] = True

        # 4. Invite Volunteers
        invite_count = self.db.query(Invitation).filter(Invitation.org_id == org_id).count()
        if invite_count > 0:
            state["invite_volunteers"] = True

        # 5. Run First Schedule (checked if assignments exist)
        assignment_count = self.db.query(Assignment).join(Event).filter(Event.org_id == org_id).count()
        if assignment_count > 0:
            state["run_schedule"] = True

        # Update if changed
        if state != progress.checklist_state:
            progress.checklist_state = state
            flag_modified(progress, "checklist_state")
            self.db.commit()
