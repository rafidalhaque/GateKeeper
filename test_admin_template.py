"""
Simple test to check if the admin page JavaScript loads correctly
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.app import create_app
from threading import Thread
import time
import requests

def run_flask_app():
    """Run Flask app in background"""
    app = create_app()
    app.run(host='0.0.0.0', port=5003, debug=False, use_reloader=False)

def test_admin_template():
    """Test if admin template loads and contains logout function"""
    BASE_URL = "http://localhost:5003"

    print("🔍 TESTING ADMIN TEMPLATE JAVASCRIPT")
    print("=" * 50)

    session = requests.Session()

    try:
        # Test login page
        print("1. Testing login page...")
        response = session.get(f"{BASE_URL}/login")
        print(f"   Status: {response.status_code}")

        if "handleLogout" in response.text:
            print("   ❌ Login page contains handleLogout (unexpected)")
        else:
            print("   ✅ Login page does NOT contain handleLogout (expected)")

        # Test admin page (will redirect to login, but we can check the redirect response)
        print("\n2. Testing admin page redirect...")
        response = session.get(f"{BASE_URL}/admin", allow_redirects=False)
        print(f"   Status: {response.status_code}")
        print(f"   Location: {response.headers.get('Location', 'None')}")

        # Test a protected admin page directly to see the template
        print("\n3. Testing admin template structure...")
        response = session.get(f"{BASE_URL}/admin/events")
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            html_content = response.text

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

            # Look for any JavaScript errors in template
            lines = html_content.split('\n')
            script_started = False
            script_lines = []

            for line_num, line in enumerate(lines, 1):
                if '<script>' in line:
                    script_started = True
                elif '</script>' in line:
                    script_started = False
                elif script_started:
                    script_lines.append(f"Line {line_num}: {line.strip()}")

            print(f"\n   JavaScript content preview (first 10 lines):")
            for line in script_lines[:10]:
                print(f"     {line}")

            if len(script_lines) > 10:
                print(f"     ... and {len(script_lines) - 10} more lines")

        else:
            print(f"   ❌ Could not load admin page: {response.status_code}")
            if response.status_code == 302:
                print(f"   Redirected to: {response.headers.get('Location')}")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting test server on port 5003...")

    # Start Flask app
    flask_thread = Thread(target=run_flask_app, daemon=True)
    flask_thread.start()

    # Wait for Flask to start
    print("⏱️  Waiting for Flask app to start...")
    time.sleep(3)

    # Run the test
    test_admin_template()

    print("\n🎯 Template test completed!")
    print("\nThis test shows what JavaScript is actually being loaded")
    print("and whether the logout functions are properly defined.")
