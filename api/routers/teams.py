"""Teams router."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from api.database import get_db
from api.dependencies import get_current_user, get_current_admin_user, verify_org_member
from api.schemas.team import (
    TeamCreate,
    TeamUpdate,
    TeamResponse,
    TeamList,
    TeamMemberAdd,
    TeamMemberRemove,
)
from api.models import Team, TeamMember, Organization, Person

router = APIRouter(prefix="/teams", tags=["teams"])


@router.post("/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(
    team_data: TeamCreate,
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new team (admin only)."""
    # Verify organization exists
    org = db.query(Organization).filter(Organization.id == team_data.org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization '{team_data.org_id}' not found",
        )

    # Verify admin belongs to the organization
    verify_org_member(current_admin, team_data.org_id)

    # Check if team already exists
    existing = db.query(Team).filter(Team.id == team_data.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Team with ID '{team_data.id}' already exists",
        )

    # Create team
    team = Team(
        id=team_data.id,
        org_id=team_data.org_id,
        name=team_data.name,
        description=team_data.description,
        extra_data=team_data.extra_data or {},
    )
    db.add(team)
    db.flush()

    # Add team members
    if team_data.member_ids:
        for person_id in team_data.member_ids:
            # Verify person exists
            person = db.query(Person).filter(Person.id == person_id).first()
            if not person:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Person '{person_id}' not found",
                )
            member = TeamMember(team_id=team.id, person_id=person_id)
            db.add(member)

    db.commit()
    db.refresh(team)

    # Get member count
    member_count = db.query(TeamMember).filter(TeamMember.team_id == team.id).count()

    response = TeamResponse.model_validate(team)
    response.member_count = member_count
    return response


@router.get("/", response_model=TeamList)
def list_teams(
    org_id: Optional[str] = Query(None, description="Filter by organization ID"),
    skip: int = 0,
    limit: int = 100,
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List teams. Users can only see teams from their own organization."""
    query = db.query(Team)

    # Enforce organization isolation
    if org_id:
        # Verify user has access to this organization
        verify_org_member(current_user, org_id)
        query = query.filter(Team.org_id == org_id)
    else:
        # Default to current user's organization
        query = query.filter(Team.org_id == current_user.org_id)

    teams = query.offset(skip).limit(limit).all()
    total = query.count()

    # Add member counts
    team_responses = []
    for team in teams:
        member_count = db.query(TeamMember).filter(TeamMember.team_id == team.id).count()
        response = TeamResponse.model_validate(team)
        response.member_count = member_count
        team_responses.append(response)

    return {"teams": team_responses, "total": total}


@router.get("/{team_id}", response_model=TeamResponse)
def get_team(
    team_id: str,
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get team by ID. Users can only view teams from their own organization."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Team '{team_id}' not found"
        )

    # Verify user belongs to the same organization
    verify_org_member(current_user, team.org_id)

    member_count = db.query(TeamMember).filter(TeamMember.team_id == team.id).count()
    response = TeamResponse.model_validate(team)
    response.member_count = member_count
    return response


@router.put("/{team_id}", response_model=TeamResponse)
def update_team(
    team_id: str,
    team_data: TeamUpdate,
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update team (admin only)."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Team '{team_id}' not found"
        )

    # Verify admin belongs to the same organization
    verify_org_member(current_admin, team.org_id)

    # Update fields
    if team_data.name is not None:
        team.name = team_data.name
    if team_data.description is not None:
        team.description = team_data.description
    if team_data.extra_data is not None:
        team.extra_data = team_data.extra_data

    db.commit()
    db.refresh(team)

    member_count = db.query(TeamMember).filter(TeamMember.team_id == team.id).count()
    response = TeamResponse.model_validate(team)
    response.member_count = member_count
    return response


@router.post("/{team_id}/members", status_code=status.HTTP_204_NO_CONTENT)
def add_team_members(
    team_id: str,
    members: TeamMemberAdd,
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Add members to team (admin only)."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Team '{team_id}' not found"
        )

    # Verify admin belongs to the same organization
    verify_org_member(current_admin, team.org_id)

    for person_id in members.person_ids:
        # Verify person exists
        person = db.query(Person).filter(Person.id == person_id).first()
        if not person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Person '{person_id}' not found"
            )

        # Verify person belongs to the same organization
        verify_org_member(current_admin, person.org_id)

        # Check if already a member
        existing = (
            db.query(TeamMember)
            .filter(TeamMember.team_id == team_id, TeamMember.person_id == person_id)
            .first()
        )
        if not existing:
            member = TeamMember(team_id=team_id, person_id=person_id)
            db.add(member)

    db.commit()
    return None


@router.delete("/{team_id}/members", status_code=status.HTTP_204_NO_CONTENT)
def remove_team_members(
    team_id: str,
    members: TeamMemberRemove,
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Remove members from team (admin only)."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Team '{team_id}' not found"
        )

    # Verify admin belongs to the same organization
    verify_org_member(current_admin, team.org_id)

    for person_id in members.person_ids:
        db.query(TeamMember).filter(
            TeamMember.team_id == team_id, TeamMember.person_id == person_id
        ).delete()

    db.commit()
    return None


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(
    team_id: str,
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete team (admin only)."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Team '{team_id}' not found"
        )

    # Verify admin belongs to the same organization
    verify_org_member(current_admin, team.org_id)

    db.delete(team)
    db.commit()
    return None
