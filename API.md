# API Documentation

## Authentication

All API endpoints (except public ticket view) require authentication using Supabase JWT tokens.

Include the token in the Authorization header:
```
Authorization: Bearer YOUR_JWT_TOKEN
```

## Base URL

```
http://localhost:5000/api
```

## Endpoints

### Events

#### Create Event
```http
POST /api/events
Content-Type: application/json

{
  "name": "Tech Conference 2024",
  "date": "2024-12-01T09:00:00Z",
  "venue": "Convention Center",
  "mode": "team",
  "passcode": "event123",
  "custom_fields": {
    "fields": [
      {"name": "dietary_preference", "type": "select", "options": ["Halal", "Vegetarian", "Vegan"]}
    ]
  }
}
```

**Response**: 201 Created
```json
{
  "id": "uuid",
  "name": "Tech Conference 2024",
  "date": "2024-12-01T09:00:00Z",
  "venue": "Convention Center",
  "mode": "team",
  "created_at": "2024-01-24T10:00:00Z"
}
```

#### List Events
```http
GET /api/events
```

**Response**: 200 OK
```json
[
  {
    "id": "uuid",
    "name": "Tech Conference 2024",
    "date": "2024-12-01T09:00:00Z",
    "venue": "Convention Center",
    "mode": "team",
    "created_at": "2024-01-24T10:00:00Z"
  }
]
```

#### Get Event
```http
GET /api/events/{event_id}
```

#### Update Event
```http
PUT /api/events/{event_id}
Content-Type: application/json

{
  "name": "Updated Event Name",
  "venue": "New Venue"
}
```

#### Delete Event
```http
DELETE /api/events/{event_id}
```

### Participants

#### Create Participant
```http
POST /api/participants
Content-Type: application/json

{
  "event_id": "uuid",
  "name": "John Doe",
  "email": "john@example.com",
  "team_id": 1,
  "t_shirt_size": "M"
}
```

#### List Participants
```http
GET /api/participants?event_id={event_id}
```

#### Update Participant
```http
PUT /api/participants/{participant_id}
Content-Type: application/json

{
  "name": "Jane Doe",
  "t_shirt_size": "L"
}
```

#### Delete Participant
```http
DELETE /api/participants/{participant_id}
```

### Teams

#### Create Team
```http
POST /api/teams
Content-Type: application/json

{
  "event_id": "uuid",
  "team_name": "Team Alpha"
}
```

#### List Teams
```http
GET /api/teams?event_id={event_id}&is_empty=false
```

#### Update Team
```http
PUT /api/teams/{team_id}
Content-Type: application/json

{
  "team_name": "Updated Team Name"
}
```

#### Delete Team
```http
DELETE /api/teams/{team_id}
```

#### Bulk Delete Empty Teams
```http
DELETE /api/teams/bulk-delete-empty?event_id={event_id}
```

### CSV Import

#### Import CSV
```http
POST /api/import/csv
Content-Type: multipart/form-data

event_id: uuid
file: [CSV file]
```

**Response**: 202 Accepted
```json
{
  "message": "CSV import job queued",
  "job_id": "task-uuid",
  "status": "queued"
}
```

#### Get Import Status
```http
GET /api/import/status/{job_id}
```

**Response**: 200 OK
```json
{
  "job_id": "task-uuid",
  "status": "completed",
  "progress": 100,
  "total_items": 50,
  "processed_items": 50,
  "error_message": null
}
```

### Check-in

#### Lookup Participant
```http
GET /api/checkin/lookup/{unique_uuid}
```

**Response**: 200 OK
```json
{
  "id": "uuid",
  "name": "John Doe",
  "email": "john@example.com",
  "attendance_status": false,
  "event": {
    "id": "uuid",
    "name": "Tech Conference 2024",
    "date": "2024-12-01T09:00:00Z"
  },
  "is_authenticated": true,
  "requires_passcode": false
}
```

#### Confirm Check-in
```http
POST /api/checkin/confirm
Content-Type: application/json

{
  "unique_uuid": "participant-uuid",
  "passcode": "event123"  // Optional if authenticated
}
```

**Response**: 200 OK
```json
{
  "message": "Check-in successful",
  "participant_id": "uuid",
  "name": "John Doe",
  "attended_at": "2024-12-01T10:30:00Z"
}
```

#### Get Check-in Logs
```http
GET /api/checkin/logs?event_id={event_id}
```

### Tickets

#### Generate Tickets
```http
POST /api/tickets/generate
Content-Type: application/json

{
  "event_id": "uuid"
}
```

**Response**: 202 Accepted
```json
{
  "message": "Ticket generation queued",
  "job_id": "task-uuid",
  "status": "queued"
}
```

#### Download Ticket
```http
GET /api/tickets/download/{unique_uuid}
```

**Response**: 200 OK (PDF file)

### Emails

#### Send Bulk Emails
```http
POST /api/email/send-bulk
Content-Type: application/json

{
  "event_id": "uuid",
  "subject": "Your Event Ticket",
  "template_name": "ticket_email"
}
```

**Response**: 202 Accepted
```json
{
  "message": "Bulk email job queued",
  "job_id": "task-uuid",
  "status": "queued",
  "recipient_count": 50
}
```

#### Retry Failed Emails
```http
POST /api/email/retry-failed
Content-Type: application/json

{
  "event_id": "uuid"
}
```

#### Get Email Logs
```http
GET /api/email/logs?event_id={event_id}
```

### Reports

#### Attendance Summary
```http
GET /api/reports/attendance-summary?event_id={event_id}
```

**Response**: 200 OK
```json
{
  "event_id": "uuid",
  "event_name": "Tech Conference 2024",
  "total_registered": 100,
  "total_attended": 85,
  "no_show": 15,
  "attendance_rate": 85.0,
  "total_teams": 20,
  "empty_teams": 2
}
```

#### Team Statistics
```http
GET /api/reports/team-stats?event_id={event_id}
```

#### Check-in Timeline
```http
GET /api/reports/checkin-timeline?event_id={event_id}
```

#### Export CSV
```http
GET /api/reports/export-csv?event_id={event_id}
```

### Admin & RBAC

#### List Permissions
```http
GET /api/admin/permissions
```

#### Create Role
```http
POST /api/admin/roles
Content-Type: application/json

{
  "name": "Event Coordinator",
  "description": "Can manage events and participants",
  "permission_ids": [1, 2, 3, 4, 5]
}
```

#### List Roles
```http
GET /api/admin/roles
```

#### Update Role
```http
PUT /api/admin/roles/{role_id}
Content-Type: application/json

{
  "name": "Updated Role Name",
  "permission_ids": [1, 2, 3]
}
```

#### Delete Role
```http
DELETE /api/admin/roles/{role_id}
```

#### List Admin Users
```http
GET /api/admin/users
```

#### Assign Role to User
```http
POST /api/admin/users/{user_id}/assign-role
Content-Type: application/json

{
  "role_id": 2
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Missing required field: name"
}
```

### 401 Unauthorized
```json
{
  "error": "Authentication required"
}
```

### 403 Forbidden
```json
{
  "error": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

## Rate Limiting

API endpoints are rate-limited to prevent abuse. Default limits:
- 10 requests per second per IP address
- Burst of 20 requests allowed

Rate limit headers:
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 8
X-RateLimit-Reset: 1640000000
```
