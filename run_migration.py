#!/usr/bin/env python
"""
Run database migrations
"""
import sys
from app.app import create_app
from flask_migrate import upgrade, current, heads

# Create app context
app = create_app()

with app.app_context():
    try:
        print("=" * 60)
        print("Current migration revision:")
        print("=" * 60)
        current()

        print("\n" + "=" * 60)
        print("Available heads:")
        print("=" * 60)
        heads()

        print("\n" + "=" * 60)
        print("Upgrading database...")
        print("=" * 60)
        upgrade()

        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
