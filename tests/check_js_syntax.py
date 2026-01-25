"""
Check for JavaScript syntax errors in admin base template
"""
import re

def check_js_syntax():
    print("🔍 JAVASCRIPT SYNTAX CHECK")
    print("=" * 30)

    try:
        # Read the admin base template
        with open('/app/templates/admin/base.html', 'r') as f:
            content = f.read()

        # Extract JavaScript content between <script> tags
        script_pattern = r'<script>(.*?)</script>'
        scripts = re.findall(script_pattern, content, re.DOTALL)

        print(f"Found {len(scripts)} script blocks")

        for i, script in enumerate(scripts):
            print(f"\nScript block {i + 1}:")
            print("-" * 20)

            lines = script.strip().split('\n')

            # Check for common syntax issues
            issues = []

            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if line:
                    # Check for unclosed strings
                    single_quotes = line.count("'") - line.count("\\'")
                    double_quotes = line.count('"') - line.count('\\"')

                    if single_quotes % 2 != 0:
                        issues.append(f"Line {line_num}: Unclosed single quote")
                    if double_quotes % 2 != 0:
                        issues.append(f"Line {line_num}: Unclosed double quote")

                    # Check for missing semicolons on important lines
                    if (line.endswith('}') and not line.endswith('};') and
                        ('function' in line or 'if' in line or 'for' in line)):
                        issues.append(f"Line {line_num}: Possible missing semicolon")

                    # Check for handleLogout definition
                    if 'window.handleLogout' in line:
                        print(f"✅ Found handleLogout definition at line {line_num}: {line[:60]}...")

            if issues:
                print("⚠️  Potential syntax issues:")
                for issue in issues:
                    print(f"  {issue}")
            else:
                print("✅ No obvious syntax errors found")

            # Show first few lines of script
            print("\nScript preview (first 5 lines):")
            for line_num, line in enumerate(lines[:5], 1):
                print(f"  {line_num:2}: {line.strip()}")

            if len(lines) > 5:
                print(f"  ... and {len(lines) - 5} more lines")

    except Exception as e:
        print(f"❌ Error reading template: {e}")

def check_nav_component():
    print("\n🔍 NAVIGATION COMPONENT CHECK")
    print("=" * 30)

    try:
        with open('/app/templates/admin/components/nav.html', 'r') as f:
            content = f.read()

        # Check for logout button
        if 'id="logoutBtn"' in content:
            print("✅ Sidebar logout button found")
        else:
            print("❌ Sidebar logout button NOT found")

        # Check for logout-btn class
        if 'logout-btn' in content:
            print("✅ logout-btn class found")
        else:
            print("❌ logout-btn class NOT found")

        # Show logout button HTML
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            if 'logoutBtn' in line or ('logout' in line.lower() and 'btn' in line.lower()):
                print(f"Line {line_num}: {line.strip()}")

    except Exception as e:
        print(f"❌ Error reading nav component: {e}")

if __name__ == "__main__":
    check_js_syntax()
    check_nav_component()
    print("\nThis checks for JavaScript syntax errors that might")
    print("prevent the logout function from being defined.")
