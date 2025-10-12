#!/usr/bin/env python3
"""
Admin User Seeding Script

This script creates the initial admin user in the database.
Run this once after setting up the database to create your admin account.

Usage:
    python seed_admin.py

Make sure to set the following environment variables in your .env file:
    - ADMIN_USERNAME
    - ADMIN_EMAIL
    - ADMIN_PASSWORD
"""

import sys
import os

# Add the parent directory to the path to import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, create_tables
from app.models.user import User, UserRole
from app.auth.utils import hash_password
from app.auth.config import AuthConfig


def seed_admin_user():
    """
    Create or update the admin user in the database.
    """
    # Create tables if they don't exist
    print("Creating database tables...")
    create_tables()

    # Create database session
    db = SessionLocal()

    try:
        # Check if admin user already exists
        existing_admin = db.query(User).filter(
            User.username == AuthConfig.ADMIN_USERNAME
        ).first()

        if existing_admin:
            print(f"Admin user '{AuthConfig.ADMIN_USERNAME}' already exists!")
            print("Updating password and email...")

            # Update existing admin
            existing_admin.email = AuthConfig.ADMIN_EMAIL
            existing_admin.hashed_password = hash_password(AuthConfig.ADMIN_PASSWORD)
            existing_admin.is_active = True
            existing_admin.role = UserRole.ADMIN

            db.commit()
            print(f"Admin user '{AuthConfig.ADMIN_USERNAME}' updated successfully!")

        else:
            print(f"Creating new admin user '{AuthConfig.ADMIN_USERNAME}'...")

            # Create new admin user
            admin_user = User(
                username=AuthConfig.ADMIN_USERNAME,
                email=AuthConfig.ADMIN_EMAIL,
                hashed_password=hash_password(AuthConfig.ADMIN_PASSWORD),
                role=UserRole.ADMIN,
                is_active=True
            )

            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)

            print(f"Admin user created successfully!")
            print(f"  Username: {admin_user.username}")
            print(f"  Email: {admin_user.email}")
            print(f"  Role: {admin_user.role.value}")
            print(f"  ID: {admin_user.id}")

    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
        sys.exit(1)

    finally:
        db.close()

    print("\nAdmin seeding complete!")
    print(f"\nYou can now login with:")
    print(f"  Username: {AuthConfig.ADMIN_USERNAME}")
    print(f"  Password: {AuthConfig.ADMIN_PASSWORD}")
    print("\nIMPORTANT: Change the default password immediately!")


if __name__ == "__main__":
    print("=" * 50)
    print("Art.OEM - Admin User Seeding")
    print("=" * 50)
    print()

    seed_admin_user()
