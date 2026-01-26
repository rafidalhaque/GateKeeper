# -*- coding: utf-8 -*-
"""
Database fix script - Add token template columns
"""
import os
os.system('chcp 65001 > nul 2>&1')  # Set UTF-8 codepage on Windows

from app.app import create_app
from app.models import db
from sqlalchemy import text, inspect

def main():
    app = create_app()

    with app.app_context():
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('events')]

        print("Current events table columns:")
        for col in columns:
            print(f"  - {col}")

        added = []

        if 'token_template_html' not in columns:
            print("\nAdding token_template_html column...")
            try:
                db.session.execute(text(
                    "ALTER TABLE events ADD COLUMN token_template_html TEXT"
                ))
                added.append('token_template_html')
                print("  OK")
            except Exception as e:
                print(f"  Error: {e}")
        else:
            print("\ntoken_template_html already exists")

        if 'token_template_css' not in columns:
            print("\nAdding token_template_css column...")
            try:
                db.session.execute(text(
                    "ALTER TABLE events ADD COLUMN token_template_css TEXT"
                ))
                added.append('token_template_css')
                print("  OK")
            except Exception as e:
                print(f"  Error: {e}")
        else:
            print("\ntoken_template_css already exists")

        if added:
            db.session.commit()
            print(f"\nSuccessfully added columns: {', '.join(added)}")
        else:
            print("\nNo columns needed to be added")

        # Verify
        columns_after = [col['name'] for col in inspector.get_columns('events')]
        token_cols = [c for c in columns_after if 'token' in c]
        print(f"\nToken-related columns: {token_cols}")

        print("\n--- DONE ---")

if __name__ == '__main__':
    main()
