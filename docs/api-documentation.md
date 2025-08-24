# API Documentation - Urdu Marsiya NER Web Application

## Table of Contents

1. [Authentication](#authentication)
2. [Base URL and Headers](#base-url-and-headers)
3. [Error Handling](#error-handling)
4. [Authentication Endpoints](#authentication-endpoints)
5. [User Management](#user-management)
6. [Project Management](#project-management)
7. [Document Management](#document-management)
8. [Entity Management](#entity-management)
9. [LLM Integration](#llm-integration)
10. [Processing Jobs](#processing-jobs)
11. [Export and Statistics](#export-and-statistics)
12. [WebSocket Events](#websocket-events)

## Authentication

The API uses JWT (JSON Web Token) authentication. All protected endpoints require a valid JWT token in the Authorization header.

### JWT Token Format

```
Authorization: Bearer <jwt_token>
```

### Token Expiration

- **Access Token**: 24 hours
- **Refresh Token**: 7 days

## Base URL and Headers

### Base URL

```
Development: http://localhost:8000
Production: https://yourdomain.com
```

### Required Headers

```http
Content-Type: application/json
Authorization: Bearer <jwt_token>
```

### Optional Headers

```http
Accept-Language: en-US
X-Requested-With: XMLHttpRequest
```

## Error Handling

### Standard Error Response Format

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {},
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

### Common HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Too Many Requests
- `500` - Internal Server Error

### Error Codes

- `AUTH_REQUIRED` - Authentication required
- `INVALID_TOKEN` - Invalid or expired token
- `PERMISSION_DENIED` - Insufficient permissions
- `VALIDATION_ERROR` - Request validation failed
- `RESOURCE_NOT_FOUND` - Requested resource not found
- `RATE_LIMIT_EXCEEDED` - API rate limit exceeded

## Authentication Endpoints

### User Login

```http
POST /api/auth/login/
```

**Request Body:**

```json
{
  "username": "user@example.com",
  "password": "securepassword"
}
```

**Response (200):**

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true
  }
}
```

### User Registration

```http
POST /api/auth/register/
```

**Request Body:**

```json
{
  "username": "user@example.com",
  "email": "user@example.com",
  "password": "securepassword",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response (201):**

```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

### Refresh Token

```http
POST /api/auth/refresh/
```

**Request Body:**

```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200):**

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### User Logout

```http
POST /api/auth/logout/
```

**Request Body:**

```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200):**

```json
{
  "message": "Successfully logged out"
}
```

## User Management

### Get User Profile

```http
GET /api/auth/profile/
```

**Response (200):**

```json
{
  "id": 1,
  "username": "user@example.com",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "bio": "Digital humanities researcher",
  "research_interests": ["Urdu Literature", "Islamic Studies"],
  "preferences": {
    "theme": "light",
    "language": "en"
  },
  "date_joined": "2024-01-01T00:00:00Z",
  "last_login": "2024-01-01T12:00:00Z"
}
```

### Update User Profile

```http
PUT /api/auth/profile/
```

**Request Body:**

```json
{
  "first_name": "John",
  "last_name": "Smith",
  "bio": "Updated bio",
  "research_interests": ["Urdu Literature", "Islamic Studies", "Poetry"]
}
```

**Response (200):**

```json
{
  "message": "Profile updated successfully",
  "user": {
    "id": 1,
    "first_name": "John",
    "last_name": "Smith",
    "bio": "Updated bio",
    "research_interests": ["Urdu Literature", "Islamic Studies", "Poetry"]
  }
}
```

## Project Management

### List Projects

```http
GET /api/projects/
```

**Query Parameters:**

- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20)
- `search` - Search term for project names
- `user` - Filter by user ID

**Response (200):**

```json
{
  "count": 5,
  "next": "http://localhost:8000/api/projects/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Karbala Marsiya Collection",
      "description": "Collection of historical Marsiya poetry",
      "users": [
        {
          "id": 1,
          "username": "user@example.com",
          "first_name": "John",
          "last_name": "Doe"
        }
      ],
      "document_count": 15,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Create Project

```http
POST /api/projects/
```

**Request Body:**

```json
{
  "name": "New Research Project",
  "description": "Project description",
  "users": [1, 2, 3]
}
```

**Response (201):**

```json
{
  "id": 2,
  "name": "New Research Project",
  "description": "Project description",
  "users": [
    {
      "id": 1,
      "username": "user@example.com",
      "first_name": "John",
      "last_name": "Doe"
    }
  ],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Get Project Details

```http
GET /api/projects/{id}/
```

**Response (200):**

```json
{
  "id": 1,
  "name": "Karbala Marsiya Collection",
  "description": "Collection of historical Marsiya poetry",
  "users": [
    {
      "id": 1,
      "username": "user@example.com",
      "first_name": "John",
      "last_name": "Doe"
    }
  ],
  "documents": [
    {
      "id": 1,
      "title": "Sample Marsiya",
      "processing_status": "completed",
      "entity_count": 25
    }
  ],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Update Project

```http
PUT /api/projects/{id}/
```

**Request Body:**

```json
{
  "name": "Updated Project Name",
  "description": "Updated description"
}
```

**Response (200):**

```json
{
  "message": "Project updated successfully",
  "project": {
    "id": 1,
    "name": "Updated Project Name",
    "description": "Updated description"
  }
}
```

### Delete Project

```http
DELETE /api/projects/{id}/
```

**Response (204):**
No content

### Get Project Statistics

```http
GET /api/projects/{id}/stats/
```

**Response (200):**

```json
{
  "total_documents": 15,
  "total_entities": 450,
  "verified_entities": 320,
  "entity_types": {
    "PERSON": 150,
    "LOCATION": 80,
    "DATE": 120,
    "TIME": 50,
    "ORGANIZATION": 30,
    "DESIGNATION": 15,
    "NUMBER": 5
  },
  "processing_status": {
    "pending": 2,
    "processing": 1,
    "completed": 12
  }
}
```

## Document Management

### List Documents

```http
GET /api/documents/
```

**Query Parameters:**

- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20)
- `project` - Filter by project ID
- `status` - Filter by processing status
- `search` - Search in document titles
- `user` - Filter by uploaded user

**Response (200):**

```json
{
  "count": 25,
  "next": "http://localhost:8000/api/documents/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Sample Marsiya Text",
      "project": {
        "id": 1,
        "name": "Karbala Marsiya Collection"
      },
      "uploaded_by": {
        "id": 1,
        "username": "user@example.com",
        "first_name": "John"
      },
      "processing_status": "completed",
      "entity_count": 25,
      "verified_entity_count": 20,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Upload Document

```http
POST /api/documents/
```

**Request Body (multipart/form-data):**

```json
{
  "title": "New Document",
  "project": 1,
  "content": "Urdu text content here...",
  "file": "(binary file data)"
}
```

**Response (201):**

```json
{
  "id": 2,
  "title": "New Document",
  "project": {
    "id": 1,
    "name": "Karbala Marsiya Collection"
  },
  "uploaded_by": {
    "id": 1,
    "username": "user@example.com"
  },
  "processing_status": "pending",
  "entity_count": 0,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Get Document Details

```http
GET /api/documents/{id}/
```

**Response (200):**

```json
{
  "id": 1,
  "title": "Sample Marsiya Text",
  "content": "Full Urdu text content...",
  "project": {
    "id": 1,
    "name": "Karbala Marsiya Collection"
  },
  "uploaded_by": {
    "id": 1,
    "username": "user@example.com"
  },
  "processing_status": "completed",
  "entity_count": 25,
  "verified_entity_count": 20,
  "file_path": "/media/documents/sample.txt",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Start NER Processing

```http
POST /api/documents/{id}/process/
```

**Request Body:**

```json
{
  "llm_model": 1,
  "processing_options": {
    "chunk_size": 1000,
    "confidence_threshold": 0.7
  }
}
```

**Response (202):**

```json
{
  "message": "Processing started",
  "job_id": 123,
  "status": "processing"
}
```

### Get Document Entities

```http
GET /api/documents/{id}/entities/
```

**Query Parameters:**

- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 100)
- `entity_type` - Filter by entity type
- `verified` - Filter by verification status
- `search` - Search in entity text

**Response (200):**

```json
{
  "count": 25,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "text": "حسین",
      "entity_type": {
        "id": 1,
        "name": "PERSON",
        "color_code": "#87CEEB"
      },
      "start_position": 15,
      "end_position": 20,
      "confidence_score": 0.95,
      "is_verified": true,
      "verified_by": {
        "id": 1,
        "username": "user@example.com"
      },
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

## Entity Management

### Create Entity

```http
POST /api/entities/
```

**Request Body:**

```json
{
  "text": "کربلا",
  "entity_type": 2,
  "document": 1,
  "start_position": 45,
  "end_position": 51,
  "confidence_score": 0.9
}
```

**Response (201):**

```json
{
  "id": 26,
  "text": "کربلا",
  "entity_type": {
    "id": 2,
    "name": "LOCATION",
    "color_code": "#90EE90"
  },
  "document": 1,
  "start_position": 45,
  "end_position": 51,
  "confidence_score": 0.9,
  "is_verified": false,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Update Entity

```http
PUT /api/entities/{id}/
```

**Request Body:**

```json
{
  "entity_type": 3,
  "start_position": 44,
  "end_position": 50
}
```

**Response (200):**

```json
{
  "message": "Entity updated successfully",
  "entity": {
    "id": 26,
    "entity_type": {
      "id": 3,
      "name": "DATE",
      "color_code": "#FFFFE0"
    },
    "start_position": 44,
    "end_position": 50
  }
}
```

### Verify Entity

```http
POST /api/entities/{id}/verify/
```

**Request Body:**

```json
{
  "verified": true,
  "notes": "Confirmed as correct"
}
```

**Response (200):**

```json
{
  "message": "Entity verified successfully",
  "entity": {
    "id": 26,
    "is_verified": true,
    "verified_by": {
      "id": 1,
      "username": "user@example.com"
    }
  }
}
```

### Bulk Verify Entities

```http
POST /api/entities/bulk-verify/
```

**Request Body:**

```json
{
  "entity_ids": [26, 27, 28],
  "verified": true,
  "notes": "Bulk verification"
}
```

**Response (200):**

```json
{
  "message": "3 entities verified successfully",
  "verified_count": 3,
  "failed_count": 0
}
```

### Delete Entity

```http
DELETE /api/entities/{id}/
```

**Response (204):**
No content

## LLM Integration

### List LLM Models

```http
GET /api/llm-models/
```

**Response (200):**

```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "name": "GPT-4",
      "provider": "openai",
      "model_name": "gpt-4",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "name": "Claude-3",
      "provider": "anthropic",
      "model_name": "claude-3-sonnet",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Create LLM Model

```http
POST /api/llm-models/
```

**Request Body:**

```json
{
  "name": "Local LLM",
  "provider": "local",
  "api_key": "local_api_key",
  "model_name": "llama-2-7b"
}
```

**Response (201):**

```json
{
  "id": 3,
  "name": "Local LLM",
  "provider": "local",
  "model_name": "llama-2-7b",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Test LLM Model

```http
POST /api/llm-models/{id}/test/
```

**Request Body:**

```json
{
  "test_text": "حسین ابن علی"
}
```

**Response (200):**

```json
{
  "success": true,
  "response_time": 1.2,
  "entities_found": 1,
  "sample_entities": [
    {
      "text": "حسین",
      "entity_type": "PERSON",
      "confidence": 0.95
    }
  ]
}
```

## Processing Jobs

### List Processing Jobs

```http
GET /api/processing/jobs/
```

**Query Parameters:**

- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20)
- `status` - Filter by job status
- `document` - Filter by document ID
- `user` - Filter by user ID

**Response (200):**

```json
{
  "count": 10,
  "results": [
    {
      "id": 123,
      "document": {
        "id": 1,
        "title": "Sample Document"
      },
      "llm_model": {
        "id": 1,
        "name": "GPT-4"
      },
      "status": "processing",
      "progress": 65,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Get Job Status

```http
GET /api/processing/jobs/{id}/status/
```

**Response (200):**

```json
{
  "id": 123,
  "status": "processing",
  "progress": 65,
  "current_step": "Processing chunk 3 of 5",
  "estimated_completion": "2024-01-01T01:00:00Z",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Cancel Job

```http
DELETE /api/processing/jobs/{id}/
```

**Response (200):**

```json
{
  "message": "Job cancelled successfully",
  "job_id": 123
}
```

## Export and Statistics

### Export to Excel

```http
GET /api/documents/{id}/export/excel/
```

**Query Parameters:**

- `include_metadata` - Include document metadata (default: true)
- `entity_types` - Filter by entity types (comma-separated)
- `verified_only` - Export only verified entities (default: false)

**Response:**

- **Content-Type**: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- **Content-Disposition**: `attachment; filename="document_export.xlsx"`
- Binary Excel file data

### Send via Email

```http
POST /api/documents/{id}/export/email/
```

**Request Body:**

```json
{
  "recipients": ["user1@example.com", "user2@example.com"],
  "subject": "Document Export",
  "message": "Please find the attached document export.",
  "format": "excel",
  "include_metadata": true
}
```

**Response (200):**

```json
{
  "message": "Export sent successfully",
  "recipients": ["user1@example.com", "user2@example.com"],
  "email_id": "email_123"
}
```

### Get Document Statistics

```http
GET /api/documents/{id}/stats/
```

**Response (200):**

```json
{
  "total_entities": 25,
  "verified_entities": 20,
  "verification_rate": 0.8,
  "entity_types": {
    "PERSON": 10,
    "LOCATION": 5,
    "DATE": 8,
    "TIME": 2
  },
  "processing_time": 45.2,
  "last_updated": "2024-01-01T12:00:00Z"
}
```

## WebSocket Events

### Connection

```javascript
const socket = new WebSocket("ws://localhost:8000/ws/processing/");
```

### Processing Progress Updates

```json
{
  "type": "processing_progress",
  "job_id": 123,
  "progress": 65,
  "current_step": "Processing chunk 3 of 5",
  "estimated_completion": "2024-01-01T01:00:00Z"
}
```

### Processing Complete

```json
{
  "type": "processing_complete",
  "job_id": 123,
  "document_id": 1,
  "entities_found": 25,
  "processing_time": 45.2
}
```

### Processing Error

```json
{
  "type": "processing_error",
  "job_id": 123,
  "error": "API rate limit exceeded",
  "retry_available": true
}
```

### Entity Updates

```json
{
  "type": "entity_updated",
  "entity_id": 26,
  "document_id": 1,
  "action": "verified",
  "user": "user@example.com"
}
```

## Rate Limiting

### Limits

- **Authentication endpoints**: 5 requests per minute
- **Document upload**: 10 requests per hour
- **LLM processing**: 5 requests per hour
- **General API**: 1000 requests per hour

### Rate Limit Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

### Rate Limit Exceeded Response

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 3600 seconds.",
    "retry_after": 3600
  }
}
```

## Pagination

### Standard Pagination Response

```json
{
  "count": 100,
  "next": "http://localhost:8000/api/documents/?page=3",
  "previous": "http://localhost:8000/api/documents/?page=1",
  "results": [...]
}
```

### Pagination Parameters

- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20, max: 100)

## Filtering and Search

### Text Search

```http
GET /api/documents/?search=کربلا
GET /api/entities/?search=حسین
```

### Date Range Filtering

```http
GET /api/documents/?created_after=2024-01-01&created_before=2024-01-31
```

### Multiple Value Filtering

```http
GET /api/entities/?entity_types=PERSON,LOCATION&verified=true
```

### Ordering

```http
GET /api/documents/?ordering=-created_at
GET /api/entities/?ordering=start_position
```

## File Upload

### Supported Formats

- **Text files**: `.txt`, `.md`
- **Document files**: `.docx`, `.pdf`
- **Maximum size**: 50MB

### Upload Response

```json
{
  "id": 1,
  "filename": "document.txt",
  "size": 1024,
  "content_type": "text/plain",
  "upload_status": "success"
}
```

## Error Responses

### Validation Error

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "title": ["This field is required."],
      "content": ["This field cannot be blank."]
    }
  }
}
```

### Permission Denied

```json
{
  "error": {
    "code": "PERMISSION_DENIED",
    "message": "You do not have permission to perform this action.",
    "details": {
      "required_permission": "can_edit_document",
      "user_permissions": ["can_view_document"]
    }
  }
}
```

### Resource Not Found

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Document with id 999 not found.",
    "details": {
      "resource_type": "Document",
      "resource_id": 999
    }
  }
}
```
