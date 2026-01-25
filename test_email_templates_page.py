"""Test email templates page rendering"""
from app.app import create_app

app = create_app()

with app.app_context():
    with app.test_request_context():
        from flask import render_template
        try:
            # Try to render the template directly
            html = render_template('admin/email_templates.html')
            print("✅ Email templates page renders successfully!")
            print(f"   HTML length: {len(html)} bytes")
        except Exception as e:
            print(f"❌ Error rendering template: {e}")
            import traceback
            traceback.print_exc()
