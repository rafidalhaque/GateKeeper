"""
Simple test to check admin base template rendering
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.app import create_app

def test_admin_base_simple():
    """Test rendering admin base template directly"""
    print("🔍 TESTING ADMIN BASE TEMPLATE")
    print("=" * 30)

    app = create_app()

    with app.app_context():
        try:
            # Test if we can render the admin base template
            from flask import render_template_string

            # Simple test template that extends admin base
            test_template = """
{% extends "admin/base.html" %}
{% block content %}
<h1>Test Content</h1>
{% endblock %}
"""

            print("1. Attempting to render admin base template...")
            rendered = render_template_string(test_template)

            print("2. Checking rendered content...")
            print(f"   Length: {len(rendered)} characters")

            # Check for logout-related content
            if "window.handleLogout" in rendered:
                print("   ✅ Contains window.handleLogout")
            else:
                print("   ❌ Does NOT contain window.handleLogout")

            if 'id="navLogoutBtn"' in rendered:
                print("   ✅ Contains navLogoutBtn")
            else:
                print("   ❌ Does NOT contain navLogoutBtn")

            if 'id="logoutBtn"' in rendered:
                print("   ✅ Contains logoutBtn")
            else:
                print("   ❌ Does NOT contain logoutBtn")

            # Show first part of rendered content
            print("\n3. Template content preview:")
            lines = rendered.split('\n')
            for i, line in enumerate(lines[:10]):
                print(f"   {i+1:2}: {line.strip()}")
            print(f"   ... and {len(lines) - 10} more lines")

            # Find script sections
            if '<script>' in rendered:
                print("\n4. Script sections found:")
                script_count = rendered.count('<script>')
                print(f"   Number of script tags: {script_count}")

                # Find the main script with handleLogout
                script_start = rendered.find('<script>')
                while script_start != -1:
                    script_end = rendered.find('</script>', script_start)
                    if script_end != -1:
                        script_content = rendered[script_start:script_end + 9]
                        if 'handleLogout' in script_content:
                            print("   Found handleLogout script:")
                            # Show just the function definition line
                            for line in script_content.split('\n'):
                                if 'handleLogout' in line:
                                    print(f"     {line.strip()}")

                    script_start = rendered.find('<script>', script_end)
            else:
                print("\n4. ❌ No script tags found in template")

        except Exception as e:
            print(f"❌ Error rendering template: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_admin_base_simple()
    print("\nThis test checks if the admin base template can be rendered")
    print("and contains the logout JavaScript when rendered directly.")
