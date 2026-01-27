#!/usr/bin/env python
"""
Test script to verify Celery configuration and task registration
Run this before starting the worker to check if everything is set up correctly
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    try:
        from app.celery_app import celery
        print("  ✅ Celery app imported")

        from app.app import create_app
        print("  ✅ Flask app factory imported")

        import app.services.tasks
        print("  ✅ Tasks module imported")

        return True
    except Exception as e:
        print(f"  ❌ Import error: {e}")
        return False


def test_celery_config():
    """Test Celery configuration"""
    print("\n🔍 Testing Celery configuration...")
    try:
        from app.celery_app import celery

        print(f"  ✅ Broker: {celery.conf.broker_url}")
        print(f"  ✅ Backend: {celery.conf.result_backend}")
        print(f"  ✅ Task modules: {celery.conf.include}")

        return True
    except Exception as e:
        print(f"  ❌ Config error: {e}")
        return False


def test_task_registration():
    """Test if tasks are registered"""
    print("\n🔍 Testing task registration...")
    try:
        from app.celery_app import celery
        from app.app import create_app
        import app.services.tasks

        # Create app context
        app = create_app()
        with app.app_context():
            # Get registered tasks
            tasks = list(celery.tasks.keys())

            # Filter out celery internal tasks
            user_tasks = [t for t in tasks if not t.startswith('celery.')]

            print(f"  Found {len(user_tasks)} user tasks:")
            for task in user_tasks:
                print(f"    ✅ {task}")

            # Check for expected tasks
            expected_tasks = [
                'app.services.tasks.generate_tickets_task',
                'app.services.tasks.import_csv_task',
                'app.services.tasks.send_bulk_emails_task'
            ]

            missing = []
            for task in expected_tasks:
                if task not in tasks:
                    missing.append(task)

            if missing:
                print(f"\n  ⚠️  Missing tasks:")
                for task in missing:
                    print(f"    ❌ {task}")
                return False

            print("\n  ✅ All expected tasks are registered!")
            return True

    except Exception as e:
        print(f"  ❌ Registration error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_redis_connection():
    """Test Redis connection"""
    print("\n🔍 Testing Redis connection...")
    try:
        import redis
        from app.config import Config

        # Parse Redis URL
        r = redis.from_url(Config.REDIS_URL)

        # Test connection
        r.ping()
        print("  ✅ Redis is accessible")

        # Get some info
        info = r.info()
        print(f"  ✅ Redis version: {info['redis_version']}")

        return True
    except Exception as e:
        print(f"  ❌ Redis connection error: {e}")
        print("  → Make sure Redis is running: redis-server")
        return False


def test_database_connection():
    """Test database connection"""
    print("\n🔍 Testing database connection...")
    try:
        from app.app import create_app
        from app.models import db

        app = create_app()
        with app.app_context():
            # Try a simple query
            db.session.execute(db.text('SELECT 1'))
            print("  ✅ Database is accessible")
            return True

    except Exception as e:
        print(f"  ❌ Database connection error: {e}")
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("  GateKeeper Celery Configuration Test")
    print("="*60)

    results = []

    results.append(("Imports", test_imports()))
    results.append(("Celery Config", test_celery_config()))
    results.append(("Task Registration", test_task_registration()))
    results.append(("Redis Connection", test_redis_connection()))
    results.append(("Database Connection", test_database_connection()))

    print("\n" + "="*60)
    print("  Test Summary")
    print("="*60)

    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {name}")
        if not passed:
            all_passed = False

    print("="*60)

    if all_passed:
        print("\n🎉 All tests passed! You can start the Celery worker now:")
        print("   celery -A celery_worker.celery worker --loglevel=info --pool=solo")
        return 0
    else:
        print("\n❌ Some tests failed. Please fix the issues above before starting the worker.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
