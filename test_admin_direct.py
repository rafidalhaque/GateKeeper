"""
Test admin template with mock session to bypass authentication
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.app import create_app
from flask import session
import uuid

def test_admin_template_direct():
    """Test admin template with mock authentication"""
    print("🔍 TESTING ADMIN TEMPLATE WITH MOCK SESSION")
    print("=" * 50)

    app = create_app()

    with app.app_context():
        # Import here to avoid circular imports
        from app.models.auth import AdminUser
        from app.models import db

        # Create a test admin user if not exists
        test_user = AdminUser.query.filter_by(email='test@example.com').first()
        if not test_user:
            test_user = AdminUser(
                email='test@example.com',
                name='Test Admin',
                is_super_admin=True,
                supabase_user_id='test-user-id'
            )
            db.session.add(test_user)
            db.session.commit()

        print(f"   Created test user: {test_user.id}")

    with app.test_client() as client:
        with client.session_transaction() as sess:
            # Use the real user ID
            sess['user_id'] = str(test_user.id)
            sess['supabase_user_id'] = 'test-user-id'

        print("1. Testing admin dashboard with mock session...")
        response = client.get('/admin')
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            html_content = response.data.decode('utf-8')

            print("2. Checking for logout-related content...")

            # Check for logout function
            if "window.handleLogout" in html_content:
                print("   ✅ Template contains window.handleLogout definition")
            else:
                print("   ❌ Template does NOT contain window.handleLogout")

            # Check for logout buttons
            if 'id="navLogoutBtn"' in html_content:
                print("   ✅ Template contains navLogoutBtn")
            else:
                print("   ❌ Template does NOT contain navLogoutBtn")

            if 'id="logoutBtn"' in html_content:
                print("   ✅ Template contains logoutBtn")
            else:
                print("   ❌ Template does NOT contain logoutBtn")

            # Check for logout-related classes
            if 'logout-btn' in html_content:
                print("   ✅ Template contains logout-btn class")
            else:
                print("   ❌ Template does NOT contain logout-btn class")

            # Check for event handlers
            if 'attachLogoutHandlers' in html_content:
                print("   ✅ Template contains attachLogoutHandlers function")
            else:
                print("   ❌ Template does NOT contain attachLogoutHandlers")

            # Extract and show JavaScript content
            print("\n3. JavaScript content analysis:")

            # Find script content
            script_start = html_content.find('<script>')
            script_end = html_content.find('</script>')

            while script_start != -1 and script_end != -1:
                script_content = html_content[script_start + 8:script_end]

                if 'handleLogout' in script_content or 'logout' in script_content.lower():
                    print("   Found logout-related script:")
                    lines = script_content.strip().split('\n')
                    for i, line in enumerate(lines[:15]):  # First 15 lines
                        print(f"     {i+1:2}: {line.strip()}")
                    if len(lines) > 15:
                        print(f"     ... and {len(lines) - 15} more lines")
                    print()

                # Find next script block
                script_start = html_content.find('<script>', script_end)
                script_end = html_content.find('</script>', script_start) if script_start != -1 else -1

            # Also check for admin/components/nav.html inclusion
            if 'admin/components/nav.html' in html_content:
                print("   ✅ Template includes admin navigation component")
            else:
                print("   ❌ Template does NOT include admin navigation component")

        else:
            print(f"   ❌ Failed to load admin page: {response.status_code}")
            if response.status_code == 302:
                print(f"   Redirect location: {response.headers.get('Location')}")

        print("\n4. Testing other admin pages...")

        # Test other admin pages
        admin_pages = [
            '/admin/events',
            '/admin/participants',
            '/admin/settings'
        ]

        for page_url in admin_pages:
            response = client.get(page_url)
            if response.status_code == 200:
                if 'window.handleLogout' in response.data.decode('utf-8'):
                    print(f"   ✅ {page_url} contains handleLogout")
                else:
                    print(f"   ❌ {page_url} does NOT contain handleLogout")
            else:
                print(f"   ❌ {page_url} returned {response.status_code}")

if __name__ == "__main__":
    test_admin_template_direct()

    print("\n🎯 Direct template test completed!")
    print()
    print("This test bypasses authentication to check if the admin")
    print("template actually contains the logout JavaScript when rendered.")
