# API Authorization Matrix

Current policy, 2026-09-14. The executable source of truth is
[`api/route_auth_policy.py`](../api/route_auth_policy.py). It names every mounted
FastAPI operation as `public`, `public-token`, `public-callback`, `member`, or
`admin`.
[`tests/unit/test_api_route_auth_policy.py`](../tests/unit/test_api_route_auth_policy.py)
compares that policy with the live route table and fails when a route is missing,
stale, or wired to the wrong authentication dependency.

## Policy Classes

| Policy | Contract |
| --- | --- |
| `public` | No credential. Limited to health, API metadata, login, atomic first-organization signup, and email availability. |
| `public-token` | No bearer JWT. The request carries a separate scoped token, such as an invitation, refresh token, calendar feed token, or password-reset token. |
| `public-callback` | No bearer JWT. Reserved for disabled-by-default provider callbacks. Twilio callbacks require an SDK-validated signature over the exact configured external URL and form fields before any state change. |
| `member` | Valid JWT for an active person. Tenant reads derive organization scope from that actor. Person-owned data permits self-service and an administrator in the same tenant. |
| `admin` | Valid JWT whose sole access role is `admin`. Organization identifiers must match the actor's tenant. |

An invalid bearer token returns `401`. A missing bearer token on protected routes
retains FastAPI HTTPBearer's `403`. An authenticated actor requesting an explicit
foreign organization receives `403`; a guessed resource identifier is looked up
inside the actor's tenant and returns `404` whether it is foreign or absent.

## Session And Tenant Binding

Every API access token and browser session cookie contains both the person `sub` and
the person's `org_id`. Authentication reloads an active person by both values; a
missing tenant claim, mismatched tenant claim, inactive membership, or deleted person
invalidates the credential. Refresh tokens already carry the same tenant and may rotate
only an active matching membership. Password changes and resets continue to revoke
older credentials through `pwd_iat` and refresh-token versioning.

An inactive person cannot log in, refresh, use an API token, or retain a browser
session. Organization cancellation is a reversible lifecycle state, not automatic
member deactivation: authenticated administrators retain the restore path during the
retention period, while cancelled organizations are omitted from normal listings.
Deletion and any later retention purge are separate operations.

## Organization Lifecycle

| Operation | Anonymous | Owning member | Owning admin | Foreign admin | State and audit contract |
| --- | --- | --- | --- | --- | --- |
| List/read | Denied | Own tenant only | Own tenant only | Requested tenant denied | Cancelled tenants are hidden by default; `include_cancelled=true` can reveal only the caller's own tenant. |
| Update | Denied | Denied | Allowed | Denied | Organization fields and one `org.updated` audit row commit together. |
| Cancel | Denied | Denied | Allowed | Denied | Set `cancelled_at` and the current 30-day retention marker, hide the tenant from the default list, and retain the authenticated admin restore path. |
| Restore | Denied | Denied | Allowed | Denied | Clear cancellation, retention, and deletion-scheduling markers and return the tenant to the default list. |
| Hard delete | Denied | Denied | Allowed | Denied | Delete the tenant's owned scheduling and delivery graph while retaining a denormalized `data.bulk_delete` audit row; leave other tenants unchanged. |

Every lifecycle mutation and its audit record share one transaction. A failed audit
write or commit rolls the mutation back. The PostgreSQL acceptance drill covers a
representative hard-delete graph containing a member, invitation, event, solution,
assignment, notification, and delivery log. `Notification.delivery_logs` is explicit
delete-orphan ownership so provider-delivery evidence cannot strand the tenant delete.

Hard delete is an explicit administrator API operation. No scheduled retention purge,
legal-hold policy, production backup deletion, or owner-approved retention policy is
implemented by this contract; those remain under #268.

Church and Basketball BO-12 browser acceptance runs both tenants in one application
process. It checks each administrator's isolated directory and signs in one member for
every declared scheduling qualification at 360px and 1440px. Those members cannot open
the administrator surface, invite, publish, inspect a foreign person, or mutate a peer's
availability. This is application-level local evidence; it does not certify deployment,
provider, or database-infrastructure isolation.

## Browser Request Integrity

Every unsafe browser request under `/auth/`, `/a/`, or `/v/` must carry both an exact
same-origin `Origin` header and a valid signed double-submit CSRF token. Standard forms
receive a hidden `csrf_token` field; HTMX requests send `X-CSRF-Token`. The middleware
derives the expected origin from `FRONTEND_URL`, then `APP_URL`, and only falls back to
the request origin for local development. Missing origins, foreign origins, missing or
mismatched tokens, and forged unsigned tokens return `403` before route code can write.

The CSRF cookie is `SameSite=Lax`, but SameSite is defense in depth rather than the
authorization decision. It is marked `Secure` in production. Bearer-token API routes
under `/api/` retain their existing authentication contract and are outside this browser
middleware. `tests/web/test_request_integrity.py` inventories unsafe browser routes and
tests no-write failures; `tests/e2e/test_request_integrity.py` verifies form injection,
same-origin HTMX success, and a rejected foreign-origin write in Chromium.

## Scheduling Surface

| Route family | Reads | Writes | Tenant and ownership rule | Regression evidence |
| --- | --- | --- | --- | --- |
| `/events` | Member for list/detail; admin for available people, validation, and organization-wide assignments | Admin | Event, resource, team, person, and assignment children must resolve inside the actor's organization before use. | `tests/api/test_scheduling_tenant_boundaries.py`, event/search and child cases |
| `/availability` | Self or same-tenant admin | Self or same-tenant admin | Load the target person through the actor's organization first; same-tenant peers receive `403`, foreign or absent people receive `404`. | `tests/api/test_scheduling_tenant_boundaries.py`, availability case |
| `/conflicts` | Admin | Admin check operation | Person, target event, existing assignments, and overlapping events are joined through the admin's organization. | `tests/api/test_scheduling_tenant_boundaries.py`, conflict case |
| `/solver` | Admin | Admin | The requested organization must equal the admin's organization; source rows are organization-filtered. | Domain playbooks and multi-tenant API tests |
| `/solutions` | Admin, including assignment snapshots, streams, statistics, and comparisons | Admin, including create, export, publish, rollback, and delete | Solutions are selected by ID plus actor organization. Assignment children require same-tenant event and person joins. | `tests/api/test_scheduling_tenant_boundaries.py`, solution and stream cases |
| `/solutions/{id}/export` | Admin | Admin | Validate `org`, `person:{id}`, or `team:{id}` before querying assignments. Filter event, person, assignment, and identity-bearing metric rows before JSON, CSV, or PDF serialization. ICS remains an explicit `501`, never a broader fallback. | `tests/api/test_scheduling_tenant_boundaries.py`, export case |

The remaining mounted operations are classified individually in the executable
policy. Public-token routes are exceptions, not evidence that a router or route
family is generally public. Billing and paid SMS remain disabled by default;
their registered operations still require the policy shown in the source when
those feature gates are enabled.

## Change Protocol

1. Add or change the route's explicit entry in `api/route_auth_policy.py`.
2. Apply actor-derived tenant and ownership filters in the route query itself.
3. Add real-JWT tests for anonymous, invalid, member, same-tenant admin, and
   foreign-admin actors where the operation can expose tenant data or mutate state.
4. Assert forbidden writes leave database state unchanged and exports receive an
   already-filtered dataset before serialization.
5. Refresh the OpenAPI snapshot and generated mobile client when the contract changes.
6. Run the matrix and scheduling regressions locally:

```bash
poetry run pytest tests/unit/test_api_route_auth_policy.py tests/api/test_access_token_tenancy.py tests/api/test_scheduling_tenant_boundaries.py tests/security/test_authentication.py -q
```

Do not use the tenancy warning listener as authorization. Every query that can
reach organization data must carry the concrete tenant predicate required by the
route's policy.
