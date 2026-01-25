"""
Playwright test for logout functionality
Tests the logout button behavior in the admin panel
"""
import asyncio
import os
from playwright.async_api import async_playwright
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.app import create_app
from threading import Thread
import time

# Test configuration
BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")
TEST_EMAIL = os.getenv("TEST_EMAIL", "ahmadmusa@tuta.io")
TEST_PASSWORD = os.getenv("TEST_PASSWORD")  # Set this in your environment if you want full testing


def run_flask_app():
    """Run Flask app in background for testing"""
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)


async def test_logout_functionality():
    """Test logout button functionality with Playwright"""
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)  # Set to True for headless mode
        context = await browser.new_context()
        page = await context.new_page()

        # Enable console logging
        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))

        # Enable network request logging
        network_requests = []
        page.on("request", lambda req: network_requests.append(f"REQUEST: {req.method} {req.url}"))
        page.on("response", lambda resp: network_requests.append(f"RESPONSE: {resp.status} {resp.url}"))

        try:
            print("🔧 Starting Playwright logout test...")
            print("=" * 50)

            # Step 1: Go to admin page (should redirect to login)
            print("1. Navigating to admin page...")
            await page.goto(f"{BASE_URL}/admin")
            await page.wait_for_load_state("networkidle")

            current_url = page.url
            print(f"   Current URL: {current_url}")

            if "/login" in current_url:
                print("   ✅ Correctly redirected to login page")
            else:
                print("   ❌ Not redirected to login - might already be logged in")

            # Step 2: Test the test-logout page directly
            print("\n2. Testing logout test page...")
            await page.goto(f"{BASE_URL}/test-logout")
            await page.wait_for_load_state("networkidle")

            # Wait a moment for JavaScript to initialize
            await page.wait_for_timeout(1000)

            print("   ✅ Logout test page loaded")

            # Step 3: Test direct API call
            print("\n3. Testing direct API logout call...")
            await page.click("#testLogout1")
            await page.wait_for_timeout(2000)  # Wait for API call to complete

            # Check console messages
            print("   Console messages after API test:")
            for msg in console_messages[-10:]:  # Last 10 messages
                print(f"     {msg}")

            # Check network requests
            recent_requests = [req for req in network_requests if "/auth/logout" in req]
            print("   Network requests containing /auth/logout:")
            for req in recent_requests[-5:]:  # Last 5 relevant requests
                print(f"     {req}")

            # Step 4: Test button simulation
            print("\n4. Testing button click simulation...")
            console_messages.clear()  # Clear previous messages
            await page.click("#testLogout2")
            await page.wait_for_timeout(2000)

            print("   Console messages after button simulation:")
            for msg in console_messages[-10:]:
                print(f"     {msg}")

            # Step 5: If we can login, test actual logout buttons
            if TEST_PASSWORD and TEST_PASSWORD != "your-test-password":
                print("\n5. Testing actual login and logout flow...")

                # Go to login page
                await page.goto(f"{BASE_URL}/login")
                await page.wait_for_load_state("networkidle")

                # Fill login form
                await page.fill("#email", TEST_EMAIL)
                await page.fill("#password", TEST_PASSWORD)

                # Clear console messages before login
                console_messages.clear()

                # Submit login
                await page.click("#loginBtn")
                await page.wait_for_timeout(3000)

                current_url = page.url
                if "/admin" in current_url:
                    print("   ✅ Successfully logged in")

                    # Wait for page to fully load and JavaScript to initialize
                    await page.wait_for_timeout(2000)

                    print("   Console messages after login:")
                    for msg in console_messages[-20:]:
                        print(f"     {msg}")

                    # Test if handleLogout function exists in admin page
                    handleLogout_exists = await page.evaluate("typeof window.handleLogout === 'function'")
                    print(f"   handleLogout function exists: {handleLogout_exists}")

                    # Check what logout buttons exist
                    logout_buttons = await page.evaluate("""
                        () => {
                            const buttons = [];
                            // Check for navbar logout button
                            const navBtn = document.getElementById('navLogoutBtn');
                            if (navBtn) buttons.push({id: 'navLogoutBtn', text: navBtn.textContent.trim(), visible: navBtn.offsetParent !== null});
                            
                            // Check for sidebar logout button  
                            const sideBtn = document.getElementById('logoutBtn');
                            if (sideBtn) buttons.push({id: 'logoutBtn', text: sideBtn.textContent.trim(), visible: sideBtn.offsetParent !== null});
                            
                            // Check for any logout-related elements
                            const allLogout = document.querySelectorAll('[data-action="logout"], .logout-btn, *[id*="logout"], *[class*="logout"]');
                            allLogout.forEach(btn => {
                                if (btn.id !== 'navLogoutBtn' && btn.id !== 'logoutBtn') {
                                    buttons.push({
                                        id: btn.id || 'no-id',
                                        class: btn.className,
                                        text: btn.textContent.trim(),
                                        tag: btn.tagName,
                                        visible: btn.offsetParent !== null
                                    });
                                }
                            });
                            
                            return buttons;
                        }
                    """)

                    print("   Found logout buttons:")
                    for btn in logout_buttons:
                        print(f"     {btn}")

                    # Clear console for logout test
                    console_messages.clear()

                    # Test navbar logout button
                    print("   Testing navbar logout button...")

                    try:
                        # First click the dropdown to reveal the logout button
                        await page.click(".dropdown label")
                        await page.wait_for_timeout(500)

                        # Check if the dropdown opened and logout button is visible
                        logout_visible = await page.is_visible("#navLogoutBtn")
                        print(f"   Navbar logout button visible after dropdown click: {logout_visible}")

                        if logout_visible:
                            # Click logout button in dropdown
                            await page.click("#navLogoutBtn")
                            await page.wait_for_timeout(3000)
                        else:
                            print("   ❌ Navbar logout button not visible, trying manual JavaScript click")
                            await page.evaluate("document.getElementById('navLogoutBtn').click()")
                            await page.wait_for_timeout(3000)

                    except Exception as e:
                        print(f"   ❌ Error clicking navbar logout: {e}")

                        # Try sidebar logout button as backup
                        print("   Trying sidebar logout button...")
                        try:
                            await page.click("#logoutBtn")
                            await page.wait_for_timeout(3000)
                        except Exception as e2:
                            print(f"   ❌ Error clicking sidebar logout: {e2}")

                            # Try manual function call
                            print("   Trying manual handleLogout call...")
                            await page.evaluate("window.handleLogout && window.handleLogout()")
                            await page.wait_for_timeout(3000)

                    final_url = page.url
                    print(f"   Final URL after logout attempts: {final_url}")

                    if "/login" in final_url:
                        print("   ✅ Logout successful!")
                    else:
                        print("   ❌ Logout failed - still on admin page")

                    print("   Console messages after logout attempts:")
                    for msg in console_messages:
                        print(f"     {msg}")

                else:
                    print("   ❌ Login failed - check credentials")
                    print(f"   Current URL: {current_url}")
                    print("   Console messages after failed login:")
                    for msg in console_messages:
                        print(f"     {msg}")
            else:
                print("\n5. Skipping actual login test (TEST_PASSWORD not set)")
                print("   To test full login flow, set TEST_PASSWORD environment variable")

            # Step 6: Summary
            print("\n6. Test Summary:")
            print("   Console messages (all):")
            for msg in console_messages:
                print(f"     {msg}")

            print("\n   Network requests summary:")
            logout_requests = [req for req in network_requests if "logout" in req.lower()]
            for req in logout_requests:
                print(f"     {req}")

        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()

        finally:
            await browser.close()
            print("\n🎯 Playwright test completed!")


async def main():
    print("🚀 Starting Flask app...")

    # Start Flask app in background thread
    flask_thread = Thread(target=run_flask_app, daemon=True)
    flask_thread.start()

    # Wait for Flask to start
    print("⏱️  Waiting for Flask app to start...")
    time.sleep(3)

    # Run the test
    await test_logout_functionality()


if __name__ == "__main__":
    print("🧪 PLAYWRIGHT LOGOUT TESTING")
    print("=" * 50)
    print()
    print("This test will:")
    print("1. Start a Flask app in the background")
    print("2. Use Playwright to navigate and test logout")
    print("3. Capture console logs and network requests")
    print("4. Test both direct API calls and button clicks")
    print()

    # Check if we need to install playwright
    try:
        import playwright
        print("✅ Playwright available")
    except ImportError:
        print("❌ Playwright not installed. Install with:")
        print("pip install playwright")
        print("playwright install")
        sys.exit(1)

    asyncio.run(main())
