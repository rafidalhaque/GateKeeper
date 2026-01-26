#!/usr/bin/env python3
"""
Test script for CSV import with custom fields functionality
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.csv_import import get_custom_field_names, validate_csv_format, process_csv_import
from app.models.events import Event
import io
import csv


def test_custom_field_extraction():
    """Test extraction of custom field names"""
    print("Testing custom field extraction...")

    # Mock event with custom fields
    class MockEvent:
        custom_fields = [
            {"name": "dietary_preference", "label": "Dietary Preference", "type": "select"},
            {"name": "emergency_contact", "label": "Emergency Contact", "type": "text"},
            {"name": "t_shirt_size", "label": "T-Shirt Size", "type": "select"}
        ]

    event = MockEvent()
    field_names = get_custom_field_names(event)

    expected = {"dietary_preference", "emergency_contact", "t_shirt_size"}
    assert field_names == expected, f"Expected {expected}, got {field_names}"
    print("✅ Custom field extraction works correctly")


def test_csv_validation_solo():
    """Test CSV validation for solo mode"""
    print("\nTesting CSV validation (solo mode)...")

    # Mock event
    class MockEvent:
        mode = 'solo'
        custom_fields = []

    event = MockEvent()

    # Valid CSV
    csv_content = "participant_name,participant_email\nJohn Doe,john@example.com"
    valid, message = validate_csv_format(event, csv_content)
    assert valid, f"Should be valid, got: {message}"
    print("✅ Valid solo CSV accepted")

    # Invalid CSV (missing columns)
    csv_content = "name,email\nJohn Doe,john@example.com"
    valid, message = validate_csv_format(event, csv_content)
    assert not valid, "Should be invalid"
    print("✅ Invalid solo CSV rejected")


def test_csv_validation_team():
    """Test CSV validation for team mode"""
    print("\nTesting CSV validation (team mode)...")

    # Mock event
    class MockEvent:
        mode = 'team'
        custom_fields = []

    event = MockEvent()

    # Valid CSV
    csv_content = "team_id,team_name,member_name,member_email\nTEAM001,Warriors,John,john@example.com"
    valid, message = validate_csv_format(event, csv_content)
    assert valid, f"Should be valid, got: {message}"
    print("✅ Valid team CSV accepted")

    # Invalid CSV (missing columns)
    csv_content = "team_id,team_name\nTEAM001,Warriors"
    valid, message = validate_csv_format(event, csv_content)
    assert not valid, "Should be invalid"
    print("✅ Invalid team CSV rejected")


def test_custom_data_extraction():
    """Test extraction of custom data from CSV row"""
    print("\nTesting custom data extraction...")

    custom_field_names = {"dietary_preference", "emergency_contact"}
    standard_columns = {"participant_name", "participant_email"}

    # Mock CSV row
    row = {
        "participant_name": "John Doe",
        "participant_email": "john@example.com",
        "dietary_preference": "Halal",
        "emergency_contact": "+1234567890",
        "unknown_column": "ignored"
    }

    # Extract custom data
    custom_data = {}
    for column_name, value in row.items():
        if column_name not in standard_columns and column_name in custom_field_names:
            custom_data[column_name] = value.strip() if value else None

    expected = {
        "dietary_preference": "Halal",
        "emergency_contact": "+1234567890"
    }

    assert custom_data == expected, f"Expected {expected}, got {custom_data}"
    print("✅ Custom data extraction works correctly")


def test_empty_values():
    """Test handling of empty custom field values"""
    print("\nTesting empty value handling...")

    custom_field_names = {"dietary_preference", "emergency_contact"}

    row = {
        "dietary_preference": "Halal",
        "emergency_contact": ""  # Empty value
    }

    custom_data = {}
    for column_name, value in row.items():
        if column_name in custom_field_names:
            custom_data[column_name] = value.strip() if value else None

    assert custom_data["emergency_contact"] is None, "Empty value should be None"
    print("✅ Empty values handled correctly (stored as None)")


def main():
    """Run all tests"""
    print("=" * 60)
    print("CSV Import with Custom Fields - Test Suite")
    print("=" * 60)

    try:
        test_custom_field_extraction()
        test_csv_validation_solo()
        test_csv_validation_team()
        test_custom_data_extraction()
        test_empty_values()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
