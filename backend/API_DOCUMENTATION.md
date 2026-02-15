# CrucibAI API Documentation

## Overview

CrucibAI provides a comprehensive REST API for building, deploying, and managing AI applications.

**Base URL:** `https://api.crucibai.com/api`

**Authentication:** All endpoints require a valid JWT token in the Authorization header.

```
Authorization: Bearer <your_jwt_token>
```

## Rate Limiting

- **Standard Tier:** 100 requests/minute
- **Pro Tier:** 1,000 requests/minute
- **Enterprise:** Custom limits

Rate limit information is included in response headers:
- `X-RateLimit-Limit`: Total requests allowed
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Unix timestamp when limit resets

## Error Handling

All errors follow a standard format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {}
  }
}
```

### Common Error Codes

- `INVALID_REQUEST`: Request validation failed
- `AUTHENTICATION_ERROR`: Invalid or missing authentication
- `AUTHORIZATION_ERROR`: Insufficient permissions
- `NOT_FOUND`: Resource not found
- `CONFLICT`: Resource already exists
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INTERNAL_ERROR`: Server error

## Endpoints

