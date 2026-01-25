#!/usr/bin/env python
"""Quick database check and update"""
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

from app.app import create_app
from app.models.auth import AdminUser
from app.models import db

def main():
    app = create_app()

    with app.app_context():
        try:
            # Get all users
            users = AdminUser.query.all()

            print("\n" + "=" * 70)
            print("CURRENT ADMIN USERS")
            print("=" * 70)

            if not users:
                print("No users found!")
                return

            for user in users:
                print(f"\nEmail: {user.email}")
                print(f"Name: {user.name}")
                print(f"Is Super Admin: {user.is_super_admin}")
                print(f"Role: {user.role.name if user.role else 'None'}")
                print("-" * 70)

            # Ask to promote
            email = 'ahmadmusa@tuta.io'
            user = AdminUser.query.filter_by(email=email).first()

            if user:
                print(f"\n{'=' * 70}")
                if not user.is_super_admin:
                    print(f"PROMOTING {email} to Super Admin...")
                    user.is_super_admin = True
                    db.session.commit()
                    print("SUCCESS! User is now a Super Admin")
                else:
                    print(f"INFO: {email} is ALREADY a Super Admin")
                print("=" * 70)
            else:
                print(f"\nERROR: User {email} not found!")

        except Exception as e:
            print(f"\nERROR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    main()
