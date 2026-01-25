"""
API documentation specification using OpenAPI 3.0
"""

SWAGGER_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "GateKeeper Event Management API",
        "description": """
# GateKeeper API Documentation

A comprehensive event management system with participant tracking, team management, and check-in functionality.

## Authentication

Most endpoints require authentication using Supabase JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Features

- **Event Management**: Create, update, and manage events
- **Participant Management**: Handle event participants and registrations
- **Team Management**: Organize participants into teams
- **Check-in System**: Real-time participant check-in tracking
- **Ticket Generation**: Unique QR code tickets for participants
- **Email Notifications**: Automated email delivery system
- **CSV Import/Export**: Bulk participant management
- **Reports**: Generate event statistics and reports

## Rate Limiting

API endpoints are rate-limited to prevent abuse. Contact the administrator if you need higher limits.
        """,
        "version": "1.0.0",
        "contact": {
            "name": "GateKeeper Support",
            "email": "support@gatekeeper.com"
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
        {"name": "Authentication", "description": "User authentication and authorization"},
        {"name": "Events", "description": "Event management operations"},
        {"name": "Participants", "description": "Participant management operations"},
        {"name": "Teams", "description": "Team management operations"},
        {"name": "Check-in", "description": "Participant check-in operations"},
        {"name": "Tickets", "description": "Ticket generation and management"},
        {"name": "Emails", "description": "Email notification system"},
        {"name": "Reports", "description": "Event statistics and reports"},
        {"name": "CSV Import", "description": "Bulk data import operations"},
        {"name": "Admin", "description": "Admin panel operations"}
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
