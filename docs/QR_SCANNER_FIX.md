# QR Code Scanner Fix

## Problem

The QR code scanner was unable to check in participants because it was getting a 400 error:

```
POST /api/checkin/confirm HTTP/1.1" 400
{"error": "Missing unique_uuid"}
```

## Root Cause

The issue had two parts:

1. **Missing UUID in API Response**: The `/api/checkin/lookup/<uuid>` endpoint was not returning the `unique_url_uuid` field in the response, so the scanner couldn't send it back during check-in confirmation.

2. **Poor Error Handling**: The scanner had minimal error handling and debugging, making it hard to diagnose the issue.

## Solution

### 1. Updated `app/routes/checkin.py`

Added `unique_url_uuid` to the lookup response:

```python
response = {
    'id': str(participant.id),
    'unique_url_uuid': str(participant.unique_url_uuid),  # ← ADDED THIS
    'name': participant.name,
    'email': participant.email,
    # ... rest of fields
}
```

### 2. Enhanced `app/templates/scanner.html`

Improved the QR code handling with:

- **Better UUID extraction**: Handles both plain UUIDs and URLs containing UUIDs
- **Comprehensive debugging**: Console logs at every step to help diagnose issues
- **Duplicate scan prevention**: Prevents scanning the same participant twice in quick succession
- **Better error messages**: Shows specific errors to users and logs details to console
- **Validation**: Checks for required data before making API calls

#### Key improvements in `handleQRCode()`:

```javascript
async handleQRCode(qrData) {
    console.log('QR Code scanned:', qrData);
    
    // Extract UUID (handles both plain UUID and URLs)
    const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    let uuid = null;
    
    if (uuidPattern.test(qrData.trim())) {
        uuid = qrData.trim();  // Plain UUID
    } else {
        // Extract from URL
        const uuidMatch = qrData.match(/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i);
        if (uuidMatch) uuid = uuidMatch[0];
    }
    
    console.log('Extracted UUID:', uuid);
    // ... rest of function
}
```

#### Key improvements in `confirmCheckin()`:

```javascript
async confirmCheckin() {
    // Validation
    if (!this.participantData || !this.participantData.unique_url_uuid) {
        console.error('Missing participant data or UUID');
        showAlert('Error: Missing participant data', 'error');
        return;
    }
    
    console.log('Confirming check-in for UUID:', this.participantData.unique_url_uuid);
    
    const payload = {
        unique_uuid: this.participantData.unique_url_uuid
    };
    
    console.log('Sending check-in payload:', payload);
    // ... rest of function
}
```

## How to Test

### 1. Generate a Test Ticket

```bash
# Use Flask CLI to generate a ticket for testing
flask --app run.py generate-ticket --participant-id <PARTICIPANT_ID>
```

Or navigate to the admin panel and generate tickets for an event.

### 2. Test the Scanner

1. **Navigate to the scanner page**: `http://localhost:5000/scanner`

2. **Click "Start Scanner"**: Allow camera access when prompted

3. **Scan a QR code from a generated ticket**

4. **Check browser console** (F12 → Console tab) for debug output:
   ```
   QR Code scanned: 123e4567-e89b-12d3-a456-426614174000
   Extracted UUID: 123e4567-e89b-12d3-a456-426614174000
   Participant data: {id: "...", name: "John Doe", ...}
   ```

5. **Verify the participant info displays** on the page

6. **Click "Mark as Attended"** (if not in quick scan mode)

7. **Check for success message**: "✓ John Doe checked in!"

### 3. Test Quick Scan Mode

1. **Enable "Quick Scan Mode"** toggle at the top

2. **Scan a QR code**

3. **Participant should be checked in automatically** without clicking a button

4. **Participant info should clear after 3 seconds**

### 4. Test Error Cases

#### Invalid QR Code
1. Scan a QR code that doesn't contain a valid UUID
2. Expected: Alert "Invalid QR code format"

#### Already Checked In
1. Scan the same participant twice
2. Expected: Alert "[Name] - Already checked in!"

#### Network Error
1. Stop the Flask server
2. Try to scan
3. Expected: Alert "Error looking up participant"

## Console Debug Output

When everything works correctly, you should see:

```javascript
QR Code scanned: 123e4567-e89b-12d3-a456-426614174000
Extracted UUID: 123e4567-e89b-12d3-a456-426614174000
Participant data: {
  id: "...",
  unique_url_uuid: "123e4567-e89b-12d3-a456-426614174000",
  name: "John Doe",
  email: "john@example.com",
  attendance_status: false,
  event: {...},
  ...
}
Confirming check-in for UUID: 123e4567-e89b-12d3-a456-426614174000
Sending check-in payload: {unique_uuid: "123e4567-e89b-12d3-a456-426614174000"}
Check-in result: {message: "Check-in successful", attended_at: "2026-01-25T12:30:45.123Z", ...}
```

## API Endpoints

### Lookup Participant
```http
GET /api/checkin/lookup/<uuid>
Authorization: Bearer <token> (optional)

Response: {
  "id": "...",
  "unique_url_uuid": "123e4567-...",  ← This field was missing before!
  "name": "John Doe",
  "email": "john@example.com",
  "attendance_status": false,
  "event": {...},
  "is_authenticated": true,
  "requires_passcode": false
}
```

### Confirm Check-in
```http
POST /api/checkin/confirm
Content-Type: application/json
Authorization: Bearer <token> (if authenticated)

{
  "unique_uuid": "123e4567-e89b-12d3-a456-426614174000"
}

Response: {
  "message": "Check-in successful",
  "participant_id": "...",
  "name": "John Doe",
  "attended_at": "2026-01-25T12:30:45.123456"
}
```

## Troubleshooting

### Still Getting "Missing unique_uuid" Error

1. **Check browser console** for the payload being sent:
   ```javascript
   Sending check-in payload: {unique_uuid: "..."}
   ```

2. **Verify the UUID exists** in participantData:
   ```javascript
   console.log(this.participantData.unique_url_uuid);
   ```

3. **Check network tab** (F12 → Network) to see the actual request body

### Scanner Not Detecting QR Code

1. **Ensure good lighting** and hold the QR code steady
2. **Try different distances** from the camera
3. **Check browser console** for error messages
4. **Verify camera permissions** are granted

### "Invalid QR code format" Error

1. **Check the QR code contains a valid UUID**:
   - Should be in format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
   - Can be a plain UUID or a URL containing a UUID

2. **Test with a known good QR code** from a generated ticket

## Related Files

- `app/routes/checkin.py` - Check-in API endpoints
- `app/templates/scanner.html` - QR scanner frontend
- `app/services/ticket_service.py` - Ticket generation with QR codes
- `app/models/events.py` - Participant model with unique_url_uuid field
