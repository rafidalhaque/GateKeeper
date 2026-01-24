#!/usr/bin/env python3
"""
Script to create a Supabase user via API (if you have service key)
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')  # Need service key for this

def create_supabase_user(email, password):
    """Create a user in Supabase Auth via API"""
    if not SUPABASE_SERVICE_KEY:
        print("❌ SUPABASE_SERVICE_KEY not found in environment")
        print("Please use the Supabase dashboard to create the user manually")
        return False

    url = f"{SUPABASE_URL}/auth/v1/admin/users"
    headers = {
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "email": email,
        "password": password,
        "email_confirm": True  # Auto-confirm email
    }

    try:
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ User created successfully!")
            print(f"   User ID: {user_data['id']}")
            print(f"   Email: {user_data['email']}")
            return True
        else:
            print(f"❌ Failed to create user: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    email = input("Enter email: ").strip()
    password = input("Enter password: ").strip()

    if email and password:
        create_supabase_user(email, password)
    else:
        print("Please provide both email and password")
