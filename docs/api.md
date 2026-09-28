# API Reference

Base URL (local): `http://localhost:8000`
Base URL (production): `<deployment URL to be added>`

All endpoints under `/transactions` require a valid JWT access token, sent as:

```
Authorization: Bearer <access_token>
```

Responses are JSON unless otherwise noted. Error responses follow FastAPI's default format:

```json
{
  "detail": "Human-readable error message"
}
```

## Authentication

### `POST /auth/register`

Creates a new user account.

**Request body**

```json
{
  "email": "user@example.com",
  "password": "a-strong-password"
}
```

**Response** `201 Created`

```json
{
  "id": "b3f1c2e4-...",
  "email": "user@example.com",
  "created_at": "2026-09-24T10:00:00Z"
}
```

**Errors**
- `400` — email already registered
- `422` — validation error (e.g. invalid email format, password too short)

---

### `POST /auth/login`

Authenticates a user and issues tokens.

**Request body**

```json
{
  "email": "user@example.com",
  "password": "a-strong-password"
}
```

**Response** `200 OK`

```json
{
  "access_token": "eyJhbGciOi...",
  "refresh_token": "eyJhbGciOi...",
  "token_type": "bearer"
}
```

**Errors**
- `401` — invalid email or password

---

### `POST /auth/refresh`

Issues a new access token from a valid refresh token.

**Request body**

```json
{
  "refresh_token": "eyJhbGciOi..."
}
```

**Response** `200 OK`

```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer"
}
```

**Errors**
- `401` — refresh token invalid or expired

---

## Transactions

All endpoints below require authentication and operate only on the records owned by the authenticated user.

### `POST /transactions/upload`

Uploads one or more screenshots for processing. Each image is classified, and transaction proofs are extracted, deduplication-checked, and stored.

**Request** — `multipart/form-data`

| Field | Type | Description |
|---|---|---|
| `files` | file[] | One or more image files (JPEG, PNG) |

**Response** `202 Accepted`

```json
{
  "batch_id": "a1b2c3d4-...",
  "files_received": 12,
  "status": "processing"
}
```

**Errors**
- `400` — no files provided, or unsupported file type
- `413` — file too large

---

### `GET /transactions/upload/{batch_id}/status`

Returns processing status for a previously submitted batch.

**Response** `200 OK`

```json
{
  "batch_id": "a1b2c3d4-...",
  "status": "completed",
  "processed": 12,
  "classified_as_transaction": 9,
  "skipped_non_transaction": 3
}
```

`status` is one of `processing`, `completed`, `failed`.

---

### `GET /transactions`

Lists the authenticated user's transactions, with optional filtering and sorting.

**Query parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `start_date` | date | none | Include records on or after this date |
| `end_date` | date | none | Include records on or before this date |
| `status` | string | none | Filter by `unreviewed`, `confirmed`, `duplicate`, `rejected` |
| `sort` | string | `date_desc` | `date_desc` or `date_asc` |
| `page` | integer | `1` | Page number |
| `page_size` | integer | `20` | Records per page, max `100` |

**Response** `200 OK`

```json
{
  "total": 47,
  "page": 1,
  "page_size": 20,
  "results": [
    {
      "id": "d4e5f6...",
      "date": "2026-09-20",
      "amount": 150000.00,
      "transaction_type": "incoming",
      "source": "GoPay",
      "counterparty": "Budi Santoso",
      "reference_id": "GP2026092000123",
      "status": "confirmed",
      "confidence_score": 0.94
    }
  ]
}
```

---

### `GET /transactions/{transaction_id}`

Retrieves a single transaction record, including its source image path.

**Response** `200 OK`

```json
{
  "id": "d4e5f6...",
  "date": "2026-09-20",
  "amount": 150000.00,
  "transaction_type": "incoming",
  "source": "GoPay",
  "counterparty": "Budi Santoso",
  "reference_id": "GP2026092000123",
  "image_path": "/storage/user_123/img_045.jpg",
  "status": "confirmed",
  "confidence_score": 0.94,
  "uploaded_at": "2026-09-20T14:32:00Z"
}
```

**Errors**
- `404` — record does not exist or does not belong to the authenticated user

---

### `PATCH /transactions/{transaction_id}` (OPTIONAL)

Updates a transaction's editable fields, typically used to correct extracted data or resolve a review flag.

**Request body** (all fields optional)

```json
{
  "amount": 150000.00,
  "counterparty": "Budi Santoso",
  "status": "confirmed"
}
```

**Response** `200 OK` — returns the updated record.

**Errors**
- `404` — record not found
- `422` — invalid field value

---

### `DELETE /transactions/{transaction_id}`

Removes a transaction record. The source image is not automatically deleted from storage.

**Response** `204 No Content`

---

### `GET /transactions/export`

Generates a downloadable report of the authenticated user's transactions.

**Query parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `format` | string | `xlsx` | `xlsx` or `pdf` |
| `start_date` | date | none | Same filtering as `GET /transactions` |
| `end_date` | date | none | Same filtering as `GET /transactions` |

**Response** `200 OK` — binary file stream with the appropriate `Content-Type` and `Content-Disposition` headers.

---

## Status Codes Summary

| Code | Meaning |
|---|---|
| `200` | Success |
| `201` | Resource created |
| `202` | Accepted for asynchronous processing |
| `204` | Success, no content returned |
| `400` | Malformed request |
| `401` | Missing or invalid authentication |
| `404` | Resource not found or not owned by the caller |
| `413` | Uploaded file exceeds size limit |
| `422` | Validation error |