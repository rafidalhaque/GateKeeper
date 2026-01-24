"""
Input validation utilities
"""
import re
from email_validator import validate_email, EmailNotValidError


def validate_email_address(email):
    """Validate email address format"""
    try:
        validated = validate_email(email, check_deliverability=False)
        return True, validated.normalized
    except EmailNotValidError as e:
        return False, str(e)


def validate_event_mode(mode):
    """Validate event mode"""
    valid_modes = ['solo', 'team']
    if mode not in valid_modes:
        return False, f"Invalid mode. Must be one of: {', '.join(valid_modes)}"
    return True, mode


def validate_uuid_format(uuid_str):
    """Validate UUID format"""
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    if not re.match(uuid_pattern, str(uuid_str).lower()):
        return False, "Invalid UUID format"
    return True, str(uuid_str)


def sanitize_string(text, max_length=None):
    """Sanitize string input"""
    if not text:
        return ""
    
    # Strip whitespace
    text = text.strip()
    
    # Limit length if specified
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text


def validate_csv_file(file):
    """Validate CSV file upload"""
    # Check if file exists
    if not file or file.filename == '':
        return False, "No file selected"
    
    # Check file extension
    if not file.filename.lower().endswith('.csv'):
        return False, "File must be in CSV format"
    
    # Check file size (max 16MB)
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    
    max_size = 16 * 1024 * 1024  # 16MB
    if file_size > max_size:
        return False, f"File size exceeds maximum allowed size of {max_size / (1024 * 1024)}MB"
    
    return True, "Valid"


def validate_password_strength(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    return True, "Valid"


def validate_phone_number(phone):
    """Validate phone number format"""
    # Simple validation - can be enhanced based on requirements
    phone = re.sub(r'\D', '', phone)  # Remove non-digits
    
    if len(phone) < 10 or len(phone) > 15:
        return False, "Invalid phone number"
    
    return True, phone


def sanitize_html(html_content):
    """Basic HTML sanitization for ticket templates"""
    # This is a basic implementation
    # In production, consider using a library like bleach
    
    # Remove potentially dangerous tags
    dangerous_tags = ['script', 'iframe', 'object', 'embed', 'form']
    
    for tag in dangerous_tags:
        html_content = re.sub(f'<{tag}[^>]*>.*?</{tag}>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
        html_content = re.sub(f'<{tag}[^>]*/?>', '', html_content, flags=re.IGNORECASE)
    
    return html_content
