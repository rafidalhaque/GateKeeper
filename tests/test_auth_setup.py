#!/usr/bin/env python3
"""
Test script to verify the new Supabase Auth login flow
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.app import create_app
from app.models import db
from app.models.auth import AdminUser, Role, Permission

def test_auth_setup():
    """Test the authentication setup"""
    app = create_app()

    with app.app_context():
        print("🔧 Testing Supabase Auth Integration Setup")
        print("=" * 50)

        # Check database models
        print("\n📊 Database Models:")
        admin_count = AdminUser.query.count()
        role_count = Role.query.count()
        perm_count = Permission.query.count()

        print(f"  - Admin Users: {admin_count}")
        print(f"  - Roles: {role_count}")
        print(f"  - Permissions: {perm_count}")

        # Check routes
        print("\n🛣️  Authentication Routes:")
        auth_routes = [rule for rule in app.url_map.iter_rules()
                      if 'auth' in str(rule.endpoint) or 'login' in str(rule.rule)]

        for route in auth_routes:
            print(f"  - {route.endpoint}: {route.rule}")

        # Check configuration
        print("\n⚙️  Configuration:")
        config_keys = ['SUPABASE_URL', 'SUPABASE_KEY', 'SUPABASE_JWT_SECRET']
        for key in config_keys:
            value = app.config.get(key, '')
            if value:
                print(f"  ✅ {key}: configured")
            else:
                print(f"  ❌ {key}: missing")

        print("\n🎉 Setup verification complete!")
        print("\nNext steps:")
        print("1. Set up your Supabase project and configure environment variables")
        print("2. Run: flask seed-permissions")
        print("3. Run: flask seed-roles")
        print("4. Run: flask create-admin --email your-email@example.com --name 'Your Name'")
        print("5. Create a user in Supabase Auth with the same email")
        print("6. Visit http://localhost:5000/admin to test login")

if __name__ == '__main__':
    test_auth_setup()
