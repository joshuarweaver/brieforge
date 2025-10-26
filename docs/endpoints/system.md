# System Endpoints

Utility endpoints for basic service checks. These routes do not require authentication.

## GET `/`

Returns a simple service banner with version metadata.

### Success Response `200 OK`

```json
{
  "message": "Fieldcraft API",
  "version": "0.1.0",
  "docs": "/docs"
}
```

## GET `/health`

Health probe used by deployment infrastructure and monitoring.

### Success Response `200 OK`

```json
{
  "status": "healthy"
}
```
