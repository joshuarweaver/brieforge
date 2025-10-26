# Authentication API

Authentication uses API keys issued per user. All requests (except registration) require an `X-API-Key` header containing a valid key for the workspace.

## POST `/api/v1/auth/register`

Create a user, bootstrap a workspace, and receive the first API key.

### Request Body

```json
{
  "email": "user@example.com",
  "workspace_name": "Optional workspace label"
}
```

- `email` *(string, required)* – login/notification email address.
- `workspace_name` *(string, optional)* – custom name for the initial workspace. Defaults to `<email local-part>'s Workspace`.

### Success Response `201 Created`

```json
{
  "api_key": "plain key value (store once)",
  "key": {
    "id": "UUID",
    "name": "Default key",
    "created_at": "ISO-8601 timestamp",
    "last_used_at": "ISO-8601 timestamp | null",
    "revoked_at": "ISO-8601 timestamp | null"
  },
  "user": {
    "id": 1,
    "email": "user@example.com",
    "workspace_id": "UUID",
    "role": "admin",
    "created_at": "ISO-8601 timestamp"
  },
  "workspace": {
    "id": "UUID",
    "name": "Workspace name",
    "owner_id": 1,
    "settings": {},
    "created_at": "ISO-8601 timestamp"
  }
}
```

The `api_key` field is only returned on creation—store it securely.

## GET `/api/v1/auth/me`

Return details for the authenticated user associated with the provided API key.

### Success Response `200 OK`

```json
{
  "id": 1,
  "email": "user@example.com",
  "workspace_id": "UUID",
  "role": "admin",
  "created_at": "ISO-8601 timestamp"
}
```

## GET `/api/v1/auth/api-keys`

List active (non-revoked) API keys for the authenticated user.

### Success Response `200 OK`

```json
[
  {
    "id": "UUID",
    "name": "Default key",
    "created_at": "ISO-8601 timestamp",
    "last_used_at": "ISO-8601 timestamp | null",
    "revoked_at": null
  }
]
```

## POST `/api/v1/auth/api-keys`

Issue an additional API key for the authenticated user.

### Request Body

```json
{
  "name": "Automation Runner"
}
```

- `name` *(string, optional)* – label for this key. Defaults to a timestamped name if absent.

### Success Response `201 Created`

```json
{
  "api_key": "plain key value",
  "key": {
    "id": "UUID",
    "name": "Automation Runner",
    "created_at": "ISO-8601 timestamp",
    "last_used_at": null,
    "revoked_at": null
  }
}
```

## DELETE `/api/v1/auth/api-keys/{key_id}`

Revoke an API key. The `{key_id}` path parameter must match a non-revoked key owned by the requester.

### Success Response `204 No Content`

Empty body. Subsequent calls to authenticated endpoints using the revoked secret will fail.
