#!/usr/bin/env python
"""
Make a user super admin
"""
import sys
from app.app import create_app
from app.models.auth import AdminUser
from app.models import db

email = 'ahmadmusa@tuta.io'

app = create_app()
with app.app_context():
    user = AdminUser.query.filter_by(email=email).first()

    if not user:
        print(f"❌ User not found: {email}")
        print("\nAvailable users:")
        for u in AdminUser.query.all():
            status = '✓ Super Admin' if u.is_super_admin else '○ Regular Admin'
            print(f'   {status} - {u.email} ({u.name})')
        sys.exit(1)

    if user.is_super_admin:
        print(f"ℹ️  User {email} is already a super admin!")
        sys.exit(0)

    # Promote to super admin
    user.is_super_admin = True
    db.session.commit()

    print("=" * 60)
    print("✅ User promoted to super admin successfully!")
    print("=" * 60)
    print(f"Email: {user.email}")
    print(f"Name: {user.name}")
    print(f"Super Admin: {user.is_super_admin}")
    print(f"Role: {user.role.name if user.role else 'None'}")
    print("=" * 60)
    print("\n⚠️  IMPORTANT: Log out and log back in for changes to take effect!")
