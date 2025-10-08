#!/usr/bin/env python3
"""
Migration script to convert SHA-256 password hashes to bcrypt.

WARNING: This will reset all user passwords to 'password' (for development only).
For production, users should reset their passwords via email.
"""

import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.models import Person
from api.security import hash_password

def migrate_passwords():
    """Migrate all SHA-256 passwords to bcrypt."""

    # Connect to database
    engine = create_engine('sqlite:///roster.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Find all users with SHA-256 hashes (64 characters, hex only)
        people = session.query(Person).all()

        sha256_count = 0
        bcrypt_count = 0

        for person in people:
            if person.password_hash and len(person.password_hash) == 64:
                # SHA-256 hash detected
                sha256_count += 1
                print(f"Converting {person.email} from SHA-256 to bcrypt...")

                # Reset to default password 'password' (for development)
                # In production, you'd send password reset emails
                person.password_hash = hash_password('password')
            elif person.password_hash and person.password_hash.startswith('$2b$'):
                # Already bcrypt
                bcrypt_count += 1

        if sha256_count > 0:
            session.commit()
            print(f"\n✅ Migration complete!")
            print(f"   Converted {sha256_count} users from SHA-256 to bcrypt")
            print(f"   {bcrypt_count} users already using bcrypt")
            print(f"\n⚠️  All migrated users now have password: 'password'")
            print(f"   Users should update their passwords after logging in")
        else:
            print(f"✅ No migration needed - all {bcrypt_count} users already using bcrypt")

    except Exception as e:
        session.rollback()
        print(f"❌ Error during migration: {e}")
        sys.exit(1)
    finally:
        session.close()

if __name__ == '__main__':
    print("🔐 Password Migration: SHA-256 → bcrypt")
    print("=" * 50)
    migrate_passwords()
