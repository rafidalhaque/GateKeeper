"""
Simple logout test using requests library
Tests the logout endpoint directly without browser automation
"""
import requests
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.app import create_app
from threading import Thread
import time

def run_flask_app():
    """Run Flask app in background for testing"""
    app = create_app()
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)

def test_logout_api():
    """Test logout API endpoint directly"""
    BASE_URL = "http://localhost:5001"

    print("🧪 TESTING LOGOUT API ENDPOINT")
    print("=" * 40)

    # Create a session to maintain cookies
    session = requests.Session()

    try:
        # Test 1: Check if server is running
        print("1. Testing server connectivity...")
        response = session.get(f"{BASE_URL}/login")
        print(f"   Login page status: {response.status_code}")

        if response.status_code != 200:
            print("   ❌ Server not responding properly")
            return
        else:
            print("   ✅ Server is running")

        # Test 2: Test logout endpoint directly
        print("\n2. Testing logout endpoint...")
        response = session.post(f"{BASE_URL}/auth/logout")
        print(f"   Logout API status: {response.status_code}")
        print(f"   Response headers: {dict(response.headers)}")

        if response.status_code == 200:
            print("   ✅ Logout API responds correctly")
            try:
                data = response.json()
                print(f"   Response data: {data}")
            except:
                print(f"   Response text: {response.text}")
        else:
            print("   ❌ Logout API failed")
            print(f"   Response text: {response.text}")

        # Test 3: Check what happens when we access admin after logout
        print("\n3. Testing admin access after logout...")
        response = session.get(f"{BASE_URL}/admin")
        print(f"   Admin page status: {response.status_code}")
        print(f"   Final URL: {response.url}")

        if response.status_code == 302 or "/login" in response.url:
            print("   ✅ Correctly redirected to login after logout")
        else:
            print("   ❌ Not properly redirected")

        # Test 4: Check user info endpoint
        print("\n4. Testing user info endpoint...")
        response = session.get(f"{BASE_URL}/auth/me")
        print(f"   User info status: {response.status_code}")

        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   User data: {data}")
                if data.get('authenticated') == False:
                    print("   ✅ Correctly shows not authenticated")
                else:
                    print("   ❌ Still shows as authenticated")
            except:
                print(f"   Response text: {response.text}")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

def test_routes_exist():
    """Test that all required routes exist"""
    BASE_URL = "http://localhost:5001"

    print("\n🔍 TESTING ROUTE AVAILABILITY")
    print("=" * 40)

    routes_to_test = [
        ("/login", "Login page"),
        ("/admin", "Admin page (should redirect)"),
        ("/test-logout", "Logout test page"),
        ("/auth/logout", "Logout API"),
        ("/auth/me", "User info API"),
    ]

    session = requests.Session()

    for route, description in routes_to_test:
        try:
            if route == "/auth/logout":
                response = session.post(f"{BASE_URL}{route}")
            else:
                response = session.get(f"{BASE_URL}{route}")

            print(f"   {description}: {response.status_code}")

            if response.status_code >= 500:
                print(f"      ❌ Server error: {response.text[:100]}")
            elif response.status_code == 404:
                print(f"      ❌ Route not found")
            else:
                print(f"      ✅ Route exists")

        except Exception as e:
            print(f"   {description}: ❌ ERROR - {e}")

if __name__ == "__main__":
    print("🚀 Starting Flask app on port 5001...")

    # Start Flask app in background thread
    flask_thread = Thread(target=run_flask_app, daemon=True)
    flask_thread.start()

    # Wait for Flask to start
    print("⏱️  Waiting for Flask app to start...")
    time.sleep(3)

    # Run the tests
    test_routes_exist()
    test_logout_api()

    print("\n🎯 API test completed!")
    print("\nNext steps:")
    print("1. If routes work, the issue is in frontend JavaScript")
    print("2. If routes fail, the issue is in backend configuration")
    print("3. Check the browser console when clicking logout buttons")
