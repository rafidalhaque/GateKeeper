"""
Enhanced Playwright test runner with environment setup
"""
import os
import asyncio
import sys

# Set test environment variables
os.environ["TEST_PASSWORD"] = "test123"  # Set this to your actual Supabase password

# Import and run the test
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_logout_playwright import test_logout_functionality
from app.app import create_app
from threading import Thread
import time

def run_flask_app():
    """Run Flask app in background for testing"""
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

async def main():
    print("🧪 ENHANCED PLAYWRIGHT LOGOUT TEST")
    print("=" * 50)
    print()
    print("Environment:")
    print(f"  BASE_URL: {os.getenv('BASE_URL', 'http://localhost:5000')}")
    print(f"  TEST_EMAIL: {os.getenv('TEST_EMAIL', 'ahmadmusa@tuta.io')}")
    print(f"  TEST_PASSWORD: {'SET' if os.getenv('TEST_PASSWORD') else 'NOT SET'}")
    print()

    # Start Flask app
    print("🚀 Starting Flask app...")
    flask_thread = Thread(target=run_flask_app, daemon=True)
    flask_thread.start()

    # Wait for Flask to start
    print("⏱️  Waiting for Flask app to start...")
    time.sleep(3)

    # Run the test
    await test_logout_functionality()

if __name__ == "__main__":
    print("IMPORTANT: Make sure to set TEST_PASSWORD to your actual Supabase password")
    print("You can either:")
    print("1. Edit line 9 in this file to set your password")
    print("2. Set TEST_PASSWORD environment variable")
    print()

    password = os.getenv("TEST_PASSWORD")
    if not password or password == "test123":
        print("⚠️  WARNING: Using default test password 'test123'")
        print("   This will only work if you've set that as your Supabase password")
        print("   Update line 9 in this file with your actual password")
        print()

    asyncio.run(main())
