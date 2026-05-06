"""Holidays router — admin-managed dates the solver can flag or skip.

Reads require authenticated org membership; writes (create / update / delete /
bulk-import) require admin in the target org.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from api.database import get_db
from api.dependencies import get_current_admin_user, get_current_user, verify_org_member
from api.models import AuditAction, Holiday, Organization, Person
from api.schemas.common import PaginationParams, get_pagination_params
from api.schemas.holiday import (
    HolidayBulkImport,
    HolidayBulkImportError,
    HolidayBulkImportResponse,
    HolidayCreate,
    HolidayList,
    HolidayResponse,
    HolidayUpdate,
)
from api.utils.audit_logger import log_audit_event

router = APIRouter(prefix="/holidays", tags=["holidays"])


@router.post("/", response_model=HolidayResponse, status_code=status.HTTP_201_CREATED)
def create_holiday(
    body: HolidayCreate,
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Create a single holiday (admin only)."""
    verify_org_member(current_admin, body.org_id)

    if not db.query(Organization).filter(Organization.id == body.org_id).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization '{body.org_id}' not found",
        )

    holiday = Holiday(
        org_id=body.org_id,
        date=body.date,
        label=body.label,
        is_long_weekend=body.is_long_weekend,
    )
    db.add(holiday)
    db.commit()
    db.refresh(holiday)
    return holiday


@router.post("/bulk", response_model=HolidayBulkImportResponse)
def bulk_import_holidays(
    body: HolidayBulkImport,
    http_request: Request,
    org_id: str = Query(..., description="Organization to import into"),
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Admin-only bulk-create holidays for one org.

    Common pattern for importing a full year's federal/diocesan calendar in one
    request. Skips dates that already have a holiday row in the target org;
    returns those as errors so the caller can decide whether to retry.
    """
    verify_org_member(current_admin, org_id)
    if not db.query(Organization).filter(Organization.id == org_id).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization '{org_id}' not found",
        )

    incoming_dates = [item.date for item in body.items]
    existing_dates = {
        d
        for (d,) in db.query(Holiday.date)
        .filter(Holiday.org_id == org_id, Holiday.date.in_(incoming_dates))
        .all()
    }

    created = 0
    skipped = 0
    errors: list[HolidayBulkImportError] = []
    seen_in_batch: set = set()

    for index, item in enumerate(body.items):
        if item.date in seen_in_batch:
            skipped += 1
            errors.append(
                HolidayBulkImportError(
                    row=index,
                    label=item.label,
                    message=f"date {item.date.isoformat()} duplicated within this batch",
                )
            )
            continue
        if item.date in existing_dates:
            skipped += 1
            errors.append(
                HolidayBulkImportError(
                    row=index,
                    label=item.label,
                    message=f"holiday on {item.date.isoformat()} already exists for this org",
                )
            )
            continue
        seen_in_batch.add(item.date)

        db.add(
            Holiday(
                org_id=org_id,
                date=item.date,
                label=item.label,
                is_long_weekend=item.is_long_weekend,
            )
        )
        created += 1

    db.commit()

    log_audit_event(
        db,
        action=AuditAction.HOLIDAY_BULK_IMPORTED,
        user_id=current_admin.id,
        user_email=current_admin.email,
        organization_id=org_id,
        resource_type="holiday",
        details={"created": created, "skipped": skipped, "errors": len(errors)},
        ip_address=http_request.client.host if http_request.client else None,
        user_agent=http_request.headers.get("user-agent"),
    )

    return HolidayBulkImportResponse(created=created, skipped=skipped, errors=errors)


@router.get("/", response_model=HolidayList)
def list_holidays(
    org_id: str = Query(..., description="Organization ID"),
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List holidays for one org. Caller must be a member."""
    verify_org_member(current_user, org_id)

    query = db.query(Holiday).filter(Holiday.org_id == org_id)
    total = query.count()
    rows = (
        query.order_by(Holiday.date.asc()).offset(pagination.offset).limit(pagination.limit).all()
    )
    return {
        "items": rows,
        "total": total,
        "limit": pagination.limit,
        "offset": pagination.offset,
    }


@router.get("/{holiday_id}", response_model=HolidayResponse)
def get_holiday(
    holiday_id: int,
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    holiday = db.query(Holiday).filter(Holiday.id == holiday_id).first()
    if not holiday:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Holiday {holiday_id} not found",
        )
    verify_org_member(current_user, holiday.org_id)
    return holiday


@router.put("/{holiday_id}", response_model=HolidayResponse)
def update_holiday(
    holiday_id: int,
    body: HolidayUpdate,
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    holiday = db.query(Holiday).filter(Holiday.id == holiday_id).first()
    if not holiday:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Holiday {holiday_id} not found",
        )
    verify_org_member(current_admin, holiday.org_id)

    if body.date is not None:
        holiday.date = body.date
    if body.label is not None:
        holiday.label = body.label
    if body.is_long_weekend is not None:
        holiday.is_long_weekend = body.is_long_weekend

    db.commit()
    db.refresh(holiday)
    return holiday


@router.delete("/{holiday_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_holiday(
    holiday_id: int,
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    holiday = db.query(Holiday).filter(Holiday.id == holiday_id).first()
    if not holiday:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Holiday {holiday_id} not found",
        )
    verify_org_member(current_admin, holiday.org_id)

    db.delete(holiday)
    db.commit()
    return None
