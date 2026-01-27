#!/usr/bin/env python3
"""
Verify Supabase Configuration
Tests if Supabase service key is properly configured and has correct permissions.
"""
import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def verify_supabase_config():
    """Verify Supabase configuration"""
    print("🔍 Verifying Supabase Configuration...\n")

    # Check environment variables
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    supabase_service_key = os.getenv('SUPABASE_SERVICE_KEY')
    supabase_jwt_secret = os.getenv('SUPABASE_JWT_SECRET')

    errors = []
    warnings = []

    # Validate SUPABASE_URL
    if not supabase_url:
        errors.append("❌ SUPABASE_URL is not set")
    elif not supabase_url.startswith('https://'):
        errors.append("❌ SUPABASE_URL should start with 'https://'")
    else:
        print(f"✅ SUPABASE_URL: {supabase_url}")

    # Validate SUPABASE_KEY (anon key)
    if not supabase_key:
        errors.append("❌ SUPABASE_KEY (anon key) is not set")
    elif not supabase_key.startswith('eyJ'):
        errors.append("❌ SUPABASE_KEY doesn't look like a valid JWT token")
    else:
        print(f"✅ SUPABASE_KEY (anon): {supabase_key[:20]}...")

    # Validate SUPABASE_SERVICE_KEY
    if not supabase_service_key:
        errors.append("❌ SUPABASE_SERVICE_KEY is not set")
    elif supabase_service_key == 'YOUR_SERVICE_ROLE_KEY_HERE':
        errors.append("❌ SUPABASE_SERVICE_KEY is still set to placeholder value")
        errors.append("   → Get the service_role key from Supabase Dashboard → Settings → API")
    elif not supabase_service_key.startswith('eyJ'):
        errors.append("❌ SUPABASE_SERVICE_KEY doesn't look like a valid JWT token")
    else:
        print(f"✅ SUPABASE_SERVICE_KEY: {supabase_service_key[:20]}...")

        # Try to use the service key to list users (test permissions)
        print("\n🧪 Testing service key permissions...")
        try:
            headers = {
                'apikey': supabase_service_key,
                'Authorization': f'Bearer {supabase_service_key}',
                'Content-Type': 'application/json'
            }

            # Try to list users (requires service_role permissions)
            response = requests.get(
                f'{supabase_url}/auth/v1/admin/users',
                headers=headers,
                params={'per_page': 1}  # Just get 1 user to test
            )

            if response.status_code == 200:
                print("✅ Service key has correct permissions (can access admin endpoints)")
                users_data = response.json()
                user_count = users_data.get('total', 'unknown')
                print(f"   Total users in Supabase Auth: {user_count}")
            elif response.status_code == 401:
                errors.append("❌ Service key authentication failed (401 Unauthorized)")
                errors.append(f"   Response: {response.text}")
            elif response.status_code == 403:
                errors.append("❌ Service key doesn't have admin permissions (403 Forbidden)")
                errors.append("   → Make sure you're using the service_role key, not the anon key")
            else:
                warnings.append(f"⚠️  Unexpected response when testing service key: {response.status_code}")
                warnings.append(f"   Response: {response.text}")

        except requests.exceptions.RequestException as e:
            errors.append(f"❌ Failed to connect to Supabase: {e}")

    # Validate SUPABASE_JWT_SECRET
    if not supabase_jwt_secret:
        warnings.append("⚠️  SUPABASE_JWT_SECRET is not set (optional, but recommended for JWT verification)")
    else:
        print(f"✅ SUPABASE_JWT_SECRET: {supabase_jwt_secret[:20]}...")

    # Print summary
    print("\n" + "="*60)
    if errors:
        print("\n❌ CONFIGURATION ERRORS:\n")
        for error in errors:
            print(error)
        print("\n📖 See SUPABASE_SERVICE_KEY_SETUP.md for detailed instructions")
        return False

    if warnings:
        print("\n⚠️  WARNINGS:\n")
        for warning in warnings:
            print(warning)

    if not errors and not warnings:
        print("\n✅ All Supabase configuration is correct!")
        print("\n🎉 You can now use the invitation system to create admin users.")

    return len(errors) == 0


if __name__ == '__main__':
    success = verify_supabase_config()
    sys.exit(0 if success else 1)
