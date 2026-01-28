"""
API documentation specification using OpenAPI 3.0
"""

SWAGGER_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "🎫 GateKeeper Event Management API",
        "description": """
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 8px; color: white; margin-bottom: 20px;">
    <h1 style="margin: 0; font-size: 28px;">Welcome to GateKeeper API</h1>
    <p style="margin: 10px 0 0 0; opacity: 0.9;">A comprehensive event management system with participant tracking, team management, and check-in functionality.</p>
</div>

## 🚀 Quick Start

1. **Authenticate**: Get your access token using `/auth/login`
2. **Create Event**: POST to `/api/events` to create a new event
3. **Add Participants**: Import participants via CSV or add individually
4. **Generate Tickets**: Create QR code tickets for participants
5. **Check-in**: Use `/api/checkin/confirm` to check in participants

## 🔐 Authentication

Most endpoints require authentication using Supabase JWT tokens. Include the token in the Authorization header:

```http
Authorization: Bearer <your-jwt-token>
```

Get your token by calling the `/auth/login` endpoint with your credentials.

## ✨ Core Features

### 📅 Event Management
Create, update, and manage events with custom fields, schedules, and configurations.

### 👥 Participant Management
Handle event participants, registrations, and bulk imports via CSV.

### 🤝 Team Management
Organize participants into teams for collaborative events and competitions.

### ✅ Check-in System
Real-time participant check-in tracking with QR code scanning support.

### 🎟️ Ticket Generation
Generate unique QR code tickets and badges for participants with custom templates.

### 📧 Email Notifications
Automated email delivery system with customizable templates.

### 📊 Reports & Analytics
Generate comprehensive event statistics, attendance reports, and insights.

### 📥 CSV Import/Export
Bulk participant management with support for custom fields.

## 📚 API Sections

- **Authentication**: User login and session management
- **Events**: CRUD operations for events
- **Participants**: Participant registration and management
- **Teams**: Team creation and member management
- **Check-in**: Real-time attendance tracking
- **Tickets**: Ticket and badge generation
- **Emails**: Email template management and delivery
- **Reports**: Statistics and analytics endpoints
- **Admin**: Administrative operations

## 🎯 Best Practices

- Always validate input data before sending requests
- Use pagination for large datasets
- Cache responses when appropriate
- Handle errors gracefully with proper status codes
- Keep your authentication tokens secure

## ⚡ Rate Limiting

API endpoints are rate-limited to ensure fair usage:
- **Standard**: 100 requests per minute
- **Authenticated**: 1000 requests per minute

Contact the administrator if you need higher limits.

## 🆘 Need Help?

- **Documentation**: Visit `/admin/settings` for guides
- **Support**: Contact support@gatekeeper.com
- **GitHub**: Report issues on our repository

<div style="margin-top: 20px; padding: 15px; background: #f0fdf4; border-left: 4px solid #22c55e; border-radius: 4px;">
    <strong>💡 Pro Tip:</strong> Use the "Try it out" feature below to test endpoints directly from this documentation!
</div>
        """,
        "version": "1.0.0",
        "contact": {
            "name": "GateKeeper Support Team",
            "email": "support@gatekeeper.com",
            "url": "https://github.com/gatekeeper/support"
        },
        "license": {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        }
    },
    "servers": [
        {
            "url": "http://localhost:5000",
            "description": "Development server"
        },
        {
            "url": "{APP_URL}",
            "description": "Production server",
            "variables": {
                "APP_URL": {
                    "default": "https://api.gatekeeper.com"
                }
            }
        }
    ],
    "tags": [
        {
            "name": "Authentication",
            "description": "🔐 User authentication and session management using Supabase JWT tokens"
        },
        {
            "name": "Events",
            "description": "📅 Create, read, update, and delete events with custom fields and schedules"
        },
        {
            "name": "Participants",
            "description": "👥 Manage event participants, registrations, and bulk imports"
        },
        {
            "name": "Teams",
            "description": "🤝 Organize participants into teams for collaborative events"
        },
        {
            "name": "Check-in",
            "description": "✅ Real-time participant check-in tracking with QR code support"
        },
        {
            "name": "Tickets",
            "description": "🎟️ Generate unique QR code tickets and badges with custom templates"
        },
        {
            "name": "Emails",
            "description": "📧 Email template management and automated notification delivery"
        },
        {
            "name": "Reports",
            "description": "📊 Generate event statistics, attendance reports, and analytics"
        },
        {
            "name": "CSV Import",
            "description": "📥 Bulk data import operations with custom field support"
        },
        {
            "name": "Admin",
            "description": "⚙️ Administrative operations and system management"
        },
        {
            "name": "Tokens",
            "description": "🆔 Generate and manage access tokens/badges for participants"
        },
        {
            "name": "SMTP",
            "description": "📮 SMTP configuration and email delivery settings"
        },
        {
            "name": "Stats",
            "description": "📈 Dashboard statistics and real-time metrics"
        },
        {
            "name": "Settings",
            "description": "⚙️ Application settings and user preferences"
        },
        {
            "name": "Image Attachments",
            "description": "🖼️ Upload and manage images for use in email templates, tickets, and tokens"
        }
    ],
    "paths": {
        "/auth/login": {
            "post": {
                "tags": ["Authentication"],
                "summary": "Authenticate user",
                "description": "Login with email and password using Supabase authentication",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["email", "password"],
                                "properties": {
                                    "email": {"type": "string", "format": "email", "example": "admin@example.com"},
                                    "password": {"type": "string", "format": "password", "example": "password123"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Login successful",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean"},
                                        "session": {"type": "object"},
                                        "user": {"type": "object"}
                                    }
                                }
                            }
                        }
                    },
                    "401": {"description": "Invalid credentials"}
                }
            }
        },
        "/auth/logout": {
            "post": {
                "tags": ["Authentication"],
                "summary": "Logout user",
                "description": "Clear user session and logout",
                "responses": {
                    "200": {
                        "description": "Logout successful",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean"},
                                        "message": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/auth/me": {
            "get": {
                "tags": ["Authentication"],
                "summary": "Get current user",
                "description": "Retrieve authenticated user information",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "User information retrieved",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "authenticated": {"type": "boolean"},
                                        "user": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "string"},
                                                "email": {"type": "string"},
                                                "name": {"type": "string"},
                                                "role": {"type": "string"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/api/events": {
            "get": {
                "tags": ["Events"],
                "summary": "List all events",
                "description": "Retrieve a list of all events",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "List of events",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {
                                        "$ref": "#/components/schemas/Event"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "post": {
                "tags": ["Events"],
                "summary": "Create new event",
                "description": "Create a new event with specified details",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/EventInput"
                            }
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "Event created successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/Event"
                                }
                            }
                        }
                    }
                }
            }
        },
        "/api/events/{event_id}": {
            "get": {
                "tags": ["Events"],
                "summary": "Get event by ID",
                "description": "Retrieve detailed information about a specific event",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "event_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string", "format": "uuid"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Event details",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/Event"
                                }
                            }
                        }
                    },
                    "404": {"description": "Event not found"}
                }
            },
            "put": {
                "tags": ["Events"],
                "summary": "Update event",
                "description": "Update an existing event",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "event_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string", "format": "uuid"}
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/EventInput"
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Event updated successfully"}
                }
            },
            "delete": {
                "tags": ["Events"],
                "summary": "Delete event",
                "description": "Delete an event and all associated data",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "event_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string", "format": "uuid"}
                    }
                ],
                "responses": {
                    "200": {"description": "Event deleted successfully"}
                }
            }
        },
        "/api/participants": {
            "get": {
                "tags": ["Participants"],
                "summary": "List participants",
                "description": "Retrieve list of all participants",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "event_id",
                        "in": "query",
                        "schema": {"type": "string", "format": "uuid"},
                        "description": "Filter by event ID"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "List of participants",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {
                                        "$ref": "#/components/schemas/Participant"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "post": {
                "tags": ["Participants"],
                "summary": "Add participant",
                "description": "Register a new participant for an event",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/ParticipantInput"
                            }
                        }
                    }
                },
                "responses": {
                    "201": {"description": "Participant registered successfully"}
                }
            }
        },
        "/api/participants/{participant_id}": {
            "get": {
                "tags": ["Participants"],
                "summary": "Get participant",
                "description": "Get participant details by ID",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "participant_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string", "format": "uuid"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Participant details",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/Participant"
                                }
                            }
                        }
                    }
                }
            },
            "put": {
                "tags": ["Participants"],
                "summary": "Update participant",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "participant_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string", "format": "uuid"}
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/ParticipantInput"
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Participant updated"}
                }
            },
            "delete": {
                "tags": ["Participants"],
                "summary": "Delete participant",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "participant_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string", "format": "uuid"}
                    }
                ],
                "responses": {
                    "200": {"description": "Participant deleted"}
                }
            }
        },
        "/api/teams": {
            "get": {
                "tags": ["Teams"],
                "summary": "List teams",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "List of teams",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {
                                        "$ref": "#/components/schemas/Team"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "post": {
                "tags": ["Teams"],
                "summary": "Create team",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/TeamInput"
                            }
                        }
                    }
                },
                "responses": {
                    "201": {"description": "Team created"}
                }
            }
        },
        "/api/checkin": {
            "post": {
                "tags": ["Check-in"],
                "summary": "Check-in participant",
                "description": "Mark participant as checked in for an event",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["unique_url_uuid"],
                                "properties": {
                                    "unique_url_uuid": {"type": "string"},
                                    "event_passcode": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Check-in successful"},
                    "404": {"description": "Participant not found"},
                    "400": {"description": "Invalid passcode or already checked in"}
                }
            }
        },
        "/api/tickets/send": {
            "post": {
                "tags": ["Tickets"],
                "summary": "Send ticket email",
                "description": "Send ticket email to participant",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["participant_id"],
                                "properties": {
                                    "participant_id": {"type": "string", "format": "uuid"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Email sent successfully"}
                }
            }
        },
        "/api/reports/event/{event_id}": {
            "get": {
                "tags": ["Reports"],
                "summary": "Get event report",
                "description": "Generate comprehensive report for an event",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "event_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string", "format": "uuid"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Event report",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "total_participants": {"type": "integer"},
                                        "checked_in": {"type": "integer"},
                                        "pending": {"type": "integer"},
                                        "teams_count": {"type": "integer"},
                                        "checkin_rate": {"type": "number"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/api/csv/import": {
            "post": {
                "tags": ["CSV Import"],
                "summary": "Import participants from CSV",
                "description": "Bulk import participants from CSV file",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "multipart/form-data": {
                            "schema": {
                                "type": "object",
                                "required": ["file", "event_id"],
                                "properties": {
                                    "file": {"type": "string", "format": "binary"},
                                    "event_id": {"type": "string", "format": "uuid"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Import successful"},
                    "400": {"description": "Invalid file format"}
                }
            }
        },
        "/api/checkin/lookup/<uuid>": {
            "get": {
                "tags": ["Check-in"],
                "summary": "Lookup participant by UUID",
                "description": "Get participant information for check-in scanning",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "uuid",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string", "format": "uuid"}
                    }
                ],
                "responses": {
                    "200": {"description": "Participant found"},
                    "404": {"description": "Participant not found"}
                }
            }
        },
        "/api/checkin/confirm": {
            "post": {
                "tags": ["Check-in"],
                "summary": "Confirm participant check-in",
                "description": "Mark participant as checked in",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["unique_url_uuid"],
                                "properties": {
                                    "unique_url_uuid": {"type": "string", "format": "uuid"},
                                    "event_passcode": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Check-in successful"},
                    "400": {"description": "Invalid passcode or already checked in"},
                    "404": {"description": "Participant not found"}
                }
            }
        },
        "/api/checkin/logs": {
            "get": {
                "tags": ["Check-in"],
                "summary": "Get check-in logs",
                "description": "Retrieve check-in audit logs for an event",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "event_id",
                        "in": "query",
                        "schema": {"type": "string", "format": "uuid"}
                    }
                ],
                "responses": {
                    "200": {"description": "Check-in logs retrieved"}
                }
            }
        },
        "/api/settings": {
            "get": {
                "tags": ["Admin"],
                "summary": "Get all settings",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {"description": "Settings retrieved"}
                }
            },
            "post": {
                "tags": ["Admin"],
                "summary": "Create setting",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["key", "value"],
                                "properties": {
                                    "key": {"type": "string"},
                                    "value": {"type": "string"},
                                    "description": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "201": {"description": "Setting created"}
                }
            }
        },
        "/api/settings/<key>": {
            "get": {
                "tags": ["Admin"],
                "summary": "Get setting by key",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {"description": "Setting retrieved"}
                }
            },
            "put": {
                "tags": ["Admin"],
                "summary": "Update setting",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["value"],
                                "properties": {
                                    "value": {"type": "string"},
                                    "description": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Setting updated"}
                }
            },
            "delete": {
                "tags": ["Admin"],
                "summary": "Delete setting",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {"description": "Setting deleted"}
                }
            }
        },
        "/api/settings/theme": {
            "get": {
                "tags": ["Admin"],
                "summary": "Get user theme preference",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "Theme preference",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "theme": {"type": "string", "enum": ["light", "dark"]}
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "put": {
                "tags": ["Admin"],
                "summary": "Update user theme preference",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["theme"],
                                "properties": {
                                    "theme": {"type": "string", "enum": ["light", "dark"]}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Theme preference updated"}
                }
            }
        },
        "/api/settings/token-printing": {
            "get": {
                "tags": ["Admin"],
                "summary": "Get token printing status",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "Token printing status",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "enabled": {"type": "boolean"}
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "put": {
                "tags": ["Admin"],
                "summary": "Update token printing setting",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["enabled"],
                                "properties": {
                                    "enabled": {"type": "boolean"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Token printing setting updated"}
                }
            }
        },
        "/api/jobs": {
            "get": {
                "tags": ["Admin"],
                "summary": "List all jobs",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {"description": "Jobs list"}
                }
            }
        },
        "/api/jobs/<task_id>": {
            "get": {
                "tags": ["Admin"],
                "summary": "Get job status",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {"description": "Job status"}
                }
            },
            "delete": {
                "tags": ["Admin"],
                "summary": "Delete job",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {"description": "Job deleted"}
                }
            }
        },
        "/api/jobs/active": {
            "get": {
                "tags": ["Admin"],
                "summary": "Get active jobs",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {"description": "Active jobs"}
                }
            }
        },
        "/api/jobs/stats": {
            "get": {
                "tags": ["Admin"],
                "summary": "Get job statistics",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {"description": "Job statistics"}
                }
            }
        },
        "/api/stats/dashboard": {
            "get": {
                "tags": ["Stats"],
                "summary": "Get dashboard statistics",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {"description": "Dashboard stats"}
                }
            }
        },
        "/api/stats/event/<event_id>": {
            "get": {
                "tags": ["Stats"],
                "summary": "Get event statistics",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {"description": "Event stats"}
                }
            }
        },
        "/api/smtp/config": {
            "get": {
                "tags": ["SMTP"],
                "summary": "Get SMTP configuration",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {"description": "SMTP config"}
                }
            },
            "post": {
                "tags": ["SMTP"],
                "summary": "Create SMTP configuration",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "201": {"description": "SMTP config created"}
                }
            }
        },
        "/api/smtp/config/test": {
            "post": {
                "tags": ["SMTP"],
                "summary": "Test SMTP configuration",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {"description": "SMTP test result"}
                }
            }
        },
        "/api/email-templates": {
            "get": {
                "tags": ["Emails"],
                "summary": "List email templates",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {"description": "Email templates"}
                }
            },
            "post": {
                "tags": ["Emails"],
                "summary": "Create email template",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "201": {"description": "Template created"}
                }
            }
        },
        "/api/email-templates/<template_id>": {
            "get": {
                "tags": ["Emails"],
                "summary": "Get email template",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {"description": "Email template"}
                }
            },
            "put": {
                "tags": ["Emails"],
                "summary": "Update email template",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {"description": "Template updated"}
                }
            },
            "delete": {
                "tags": ["Emails"],
                "summary": "Delete email template",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {"description": "Template deleted"}
                }
            }
        },
        "/api/invitations": {
            "get": {
                "tags": ["Admin"],
                "summary": "List invitations",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {"description": "Invitations list"}
                }
            },
            "post": {
                "tags": ["Admin"],
                "summary": "Create invitation",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "201": {"description": "Invitation created"}
                }
            }
        },
        "/api/invitations/<invitation_id>": {
            "delete": {
                "tags": ["Admin"],
                "summary": "Delete invitation",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {"description": "Invitation deleted"}
                }
            }
        },
        "/api/admin/roles": {
            "get": {
                "tags": ["Admin"],
                "summary": "List roles",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {"description": "Roles list"}
                }
            },
            "post": {
                "tags": ["Admin"],
                "summary": "Create role",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "201": {"description": "Role created"}
                }
            }
        },
        "/api/admin/roles/<role_id>": {
            "get": {
                "tags": ["Admin"],
                "summary": "Get role",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {"description": "Role details"}
                }
            },
            "put": {
                "tags": ["Admin"],
                "summary": "Update role",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {"description": "Role updated"}
                }
            },
            "delete": {
                "tags": ["Admin"],
                "summary": "Delete role",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {"description": "Role deleted"}
                }
            }
        },
        "/api/admin/permissions": {
            "get": {
                "tags": ["Admin"],
                "summary": "List permissions",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {"description": "Permissions list"}
                }
            }
        },
        "/api/admin/users": {
            "get": {
                "tags": ["Admin"],
                "summary": "List admin users",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {"description": "Users list"}
                }
            }
        },
        "/api/admin/users/<user_id>/assign-role": {
            "post": {
                "tags": ["Admin"],
                "summary": "Assign role to user",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {"description": "Role assigned"}
                }
            }
        },
        "/api/attachments/upload": {
            "post": {
                "tags": ["Image Attachments"],
                "summary": "Upload an image attachment",
                "description": "Upload an image to use in email templates, tickets, or tokens. Supports PNG, JPG, GIF, SVG (max 5MB)",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "multipart/form-data": {
                            "schema": {
                                "type": "object",
                                "required": ["file"],
                                "properties": {
                                    "file": {
                                        "type": "string",
                                        "format": "binary",
                                        "description": "Image file (PNG, JPG, GIF, SVG)"
                                    },
                                    "description": {
                                        "type": "string",
                                        "description": "Optional description of the image",
                                        "example": "Company Logo"
                                    },
                                    "usage_type": {
                                        "type": "string",
                                        "enum": ["email", "ticket", "token", "all"],
                                        "default": "all",
                                        "description": "Where this image will be used"
                                    }
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "Image uploaded successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean"},
                                        "message": {"type": "string"},
                                        "attachment": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "string"},
                                                "filename": {"type": "string"},
                                                "original_filename": {"type": "string"},
                                                "content_type": {"type": "string"},
                                                "file_size": {"type": "integer"},
                                                "cid": {"type": "string", "description": "Content-ID for email embedding"},
                                                "url": {"type": "string"},
                                                "html_img_tag": {"type": "string", "description": "Ready-to-use HTML img tag"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "400": {"description": "Invalid file or file too large"},
                    "401": {"description": "Authentication required"},
                    "403": {"description": "Insufficient permissions"}
                }
            }
        },
        "/api/attachments/": {
            "get": {
                "tags": ["Image Attachments"],
                "summary": "List all image attachments",
                "description": "Retrieve all uploaded images with optional filtering by usage type",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "usage_type",
                        "in": "query",
                        "schema": {
                            "type": "string",
                            "enum": ["email", "ticket", "token", "all"]
                        },
                        "description": "Filter by usage type"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "List of attachments",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean"},
                                        "attachments": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "id": {"type": "string"},
                                                    "filename": {"type": "string"},
                                                    "original_filename": {"type": "string"},
                                                    "cid": {"type": "string"},
                                                    "description": {"type": "string"},
                                                    "usage_type": {"type": "string"},
                                                    "url": {"type": "string"},
                                                    "created_at": {"type": "string", "format": "date-time"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "401": {"description": "Authentication required"}
                }
            }
        },
        "/api/attachments/<attachment_id>": {
            "get": {
                "tags": ["Image Attachments"],
                "summary": "Get attachment details",
                "description": "Retrieve detailed information about a specific image attachment",
                "parameters": [
                    {
                        "name": "attachment_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Attachment ID"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Attachment details",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean"},
                                        "attachment": {"type": "object"}
                                    }
                                }
                            }
                        }
                    },
                    "404": {"description": "Attachment not found"}
                }
            },
            "put": {
                "tags": ["Image Attachments"],
                "summary": "Update attachment metadata",
                "description": "Update description or usage type of an image attachment",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "attachment_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"}
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "description": {"type": "string"},
                                    "usage_type": {
                                        "type": "string",
                                        "enum": ["email", "ticket", "token", "all"]
                                    }
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Attachment updated successfully"},
                    "404": {"description": "Attachment not found"},
                    "401": {"description": "Authentication required"}
                }
            },
            "delete": {
                "tags": ["Image Attachments"],
                "summary": "Delete attachment",
                "description": "Soft delete an image attachment (can be recovered by admin)",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "attachment_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"}
                    }
                ],
                "responses": {
                    "200": {"description": "Attachment deleted successfully"},
                    "404": {"description": "Attachment not found"},
                    "401": {"description": "Authentication required"}
                }
            }
        },
        "/api/attachments/image/<attachment_id>": {
            "get": {
                "tags": ["Image Attachments"],
                "summary": "Serve image file",
                "description": "Get the actual image file for display or download",
                "parameters": [
                    {
                        "name": "attachment_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Image file",
                        "content": {
                            "image/*": {
                                "schema": {
                                    "type": "string",
                                    "format": "binary"
                                }
                            }
                        }
                    },
                    "404": {"description": "Image not found"}
                }
            }
        }
    },
    "components": {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        },
        "schemas": {
            "Event": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "format": "uuid"},
                    "name": {"type": "string", "example": "Tech Conference 2026"},
                    "date": {"type": "string", "format": "date-time"},
                    "venue": {"type": "string", "example": "Convention Center"},
                    "mode": {"type": "string", "enum": ["solo", "team"], "example": "solo"},
                    "passcode": {"type": "string", "nullable": True},
                    "created_at": {"type": "string", "format": "date-time"},
                    "updated_at": {"type": "string", "format": "date-time"}
                }
            },
            "EventInput": {
                "type": "object",
                "required": ["name", "date", "mode"],
                "properties": {
                    "name": {"type": "string", "minLength": 1},
                    "date": {"type": "string", "format": "date"},
                    "venue": {"type": "string"},
                    "mode": {"type": "string", "enum": ["solo", "team"]},
                    "passcode": {"type": "string"}
                }
            },
            "Participant": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "format": "uuid"},
                    "name": {"type": "string"},
                    "email": {"type": "string", "format": "email"},
                    "phone": {"type": "string"},
                    "event_id": {"type": "string", "format": "uuid"},
                    "team_id": {"type": "string", "format": "uuid", "nullable": True},
                    "checked_in": {"type": "boolean"},
                    "checkin_time": {"type": "string", "format": "date-time", "nullable": True},
                    "unique_url_uuid": {"type": "string", "format": "uuid"},
                    "created_at": {"type": "string", "format": "date-time"}
                }
            },
            "ParticipantInput": {
                "type": "object",
                "required": ["name", "email", "event_id"],
                "properties": {
                    "name": {"type": "string", "minLength": 1},
                    "email": {"type": "string", "format": "email"},
                    "phone": {"type": "string"},
                    "event_id": {"type": "string", "format": "uuid"},
                    "team_id": {"type": "string", "format": "uuid"}
                }
            },
            "Team": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "format": "uuid"},
                    "team_name": {"type": "string"},
                    "event_id": {"type": "string", "format": "uuid"},
                    "created_at": {"type": "string", "format": "date-time"}
                }
            },
            "TeamInput": {
                "type": "object",
                "required": ["team_name", "event_id"],
                "properties": {
                    "team_name": {"type": "string", "minLength": 1},
                    "event_id": {"type": "string", "format": "uuid"}
                }
            }
        }
    }
}
