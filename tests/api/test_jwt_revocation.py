"""JWT session-invalidation-on-password-change tests (Sprint 4 PR 4.4).

Tokens carry a `pwd_iat` claim. `get_current_user` rejects any token whose
`pwd_iat` is strictly older than the user's `password_changed_at`. Tokens
without the claim still validate (backward compat).
"""

from datetime import datetime, timedelta

import pytest

from api.models import Person
from api.security import create_access_token
from tests.api.conftest import auth_headers, login, seed_org, seed_user


@pytest.mark.no_mock_auth
class TestPasswordChangedAt:
    def test_signup_sets_password_changed_at(self, client, db):
        seed_org(client, "rev-signup")
        seed_user(client, "rev-signup", email="u@o.org", name="U", password="Pass1234!")

        person = db.query(Person).filter(Person.email == "u@o.org").first()
        assert person.password_changed_at is not None

    def test_token_without_pwd_iat_still_validates(self, client, db):
        seed_org(client, "rev-legacy")
        seed_user(client, "rev-legacy", email="l@o.org", name="L", password="Pass1234!")
        person = db.query(Person).filter(Person.email == "l@o.org").first()

        # Token minted directly without pwd_iat — emulates a pre-rollout token.
        legacy_token = create_access_token(data={"sub": person.id})
        resp = client.get(
            "/api/v1/people/me",
            headers={"Authorization": f"Bearer {legacy_token}"},
        )
        assert resp.status_code == 200, resp.text

    def test_login_token_works(self, client, db):
        seed_org(client, "rev-login")
        seed_user(client, "rev-login", email="ok@o.org", name="OK", password="Pass1234!")
        hdrs = auth_headers(client, email="ok@o.org", password="Pass1234!")

        resp = client.get("/api/v1/people/me", headers=hdrs)
        assert resp.status_code == 200

    def test_token_older_than_password_change_rejected(self, client, db):
        seed_org(client, "rev-old")
        seed_user(client, "rev-old", email="x@o.org", name="X", password="Pass1234!")
        # Mint a token with pwd_iat in the past (pre-password-change).
        person = db.query(Person).filter(Person.email == "x@o.org").first()
        old_pwd_iat = (datetime.utcnow() - timedelta(hours=2)).timestamp()
        old_token = create_access_token(data={"sub": person.id, "pwd_iat": old_pwd_iat})

        # Bump password_changed_at to "now" — newer than the token's pwd_iat.
        person.password_changed_at = datetime.utcnow()
        db.commit()

        resp = client.get(
            "/api/v1/people/me",
            headers={"Authorization": f"Bearer {old_token}"},
        )
        assert resp.status_code == 401

    def test_token_at_or_after_password_change_accepted(self, client, db):
        seed_org(client, "rev-fresh")
        seed_user(client, "rev-fresh", email="y@o.org", name="Y", password="Pass1234!")
        person = db.query(Person).filter(Person.email == "y@o.org").first()
        # password_changed_at set in the past
        person.password_changed_at = datetime.utcnow() - timedelta(hours=1)
        db.commit()

        # Token with pwd_iat AT password change time.
        token = create_access_token(
            data={
                "sub": person.id,
                "pwd_iat": person.password_changed_at.timestamp(),
            }
        )
        resp = client.get(
            "/api/v1/people/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200, resp.text

    def test_password_reset_invalidates_old_tokens(self, client, db):
        import os

        seed_org(client, "rev-reset")
        seed_user(client, "rev-reset", email="r@o.org", name="R", password="OldPass1!")
        old_hdrs = auth_headers(client, email="r@o.org", password="OldPass1!")

        # Old token works initially.
        assert client.get("/api/v1/people/me", headers=old_hdrs).status_code == 200

        # Trigger password reset.
        os.environ["DEBUG_RETURN_RESET_TOKEN"] = "true"
        try:
            resp = client.post("/api/v1/auth/forgot-password", json={"email": "r@o.org"})
            token = resp.json().get("token")
            assert token, resp.text
            resp = client.post(
                "/api/v1/auth/reset-password",
                json={"token": token, "new_password": "NewPass1!"},
            )
            assert resp.status_code == 200, resp.text
        finally:
            os.environ.pop("DEBUG_RETURN_RESET_TOKEN", None)

        # Old token should now be rejected.
        resp = client.get("/api/v1/people/me", headers=old_hdrs)
        assert resp.status_code == 401

        # Fresh login produces a working token.
        new_hdrs = auth_headers(client, email="r@o.org", password="NewPass1!")
        assert client.get("/api/v1/people/me", headers=new_hdrs).status_code == 200

    def test_login_includes_pwd_iat_claim(self, client, db):
        from jose import jwt

        from api.security import ALGORITHM, SECRET_KEY

        seed_org(client, "rev-claim")
        seed_user(client, "rev-claim", email="c@o.org", name="C", password="Pass1234!")
        data = login(client, email="c@o.org", password="Pass1234!")

        payload = jwt.decode(data["token"], SECRET_KEY, algorithms=[ALGORITHM])
        assert "pwd_iat" in payload
