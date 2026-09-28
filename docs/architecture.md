# Architecture Documentation

This document describes the technical design of LedgerLens in detail, expanding on the pipeline summary in the main README.

## Table of Contents

- [Design Goals](#design-goals)
- [Pipeline Stages in Detail](#pipeline-stages-in-detail)
- [Data Validation Strategy](#data-validation-strategy)
- [Deduplication Strategy](#deduplication-strategy)
- [Database Schema](#database-schema)
- [Cost and Performance Considerations](#cost-and-performance-considerations)
- [Known Limitations](#known-limitations)
- [Design Decisions and Trade-offs](#design-decisions-and-trade-offs)

## Design Goals

1. Minimize user effort: a single upload action should replace manual sorting, reading, and recording.
2. Do not silently trust AI output: every extracted field is validated, and low-confidence results are surfaced rather than hidden.
3. Avoid irreversible automated actions: suspected duplicates are flagged, never deleted, without user confirmation.
4. Keep the stack simple and fully within Python, appropriate for a solo developer working under a limited timeline.

## Pipeline Stages in Detail

### Stage 1: Upload and Preprocess

**Input:** Raw image files selected by the user (JPEG, PNG).

**Process:**
- Images are resized so the longest side does not exceed the input limit of the vision API in use (commonly 1568px).
- Images are compressed to reduce payload size and upload latency.

**Output:** A list of preprocessed images ready for classification.

**Library:** Pillow. Uploaded files arrive via a `multipart/form-data` request to `POST /transactions/upload` (see `docs/API.md`).

### Stage 2: Classification

**Input:** A single preprocessed image.

**Process:** The image is sent to a vision-capable language model with a system prompt instructing it to return a strict JSON object indicating whether the image is a proof-of-payment screenshot, along with a confidence score and a coarse type label (bank transfer, QRIS, e-wallet, receipt, or unknown).

**Output:** A boolean classification result with confidence score.

**Rationale for using a vision-language model instead of a trained image classifier:** training a convolutional model from scratch requires a labeled dataset and training time that are not feasible within a short development window. A vision-language model performs this classification with no additional training required, at the cost of a higher per-image inference cost compared to a lightweight local classifier.

### Stage 3: Extraction

**Input:** An image confirmed as a transaction proof in Stage 2.

**Process:** The same or a follow-up call to the vision model requests structured extraction of specific fields, constrained to a defined schema. The model is explicitly instructed not to infer or fabricate values that are not visible in the image; missing fields are returned as null rather than guessed.

**Output:** A structured transaction object, prior to validation.

**Optimization note:** classification and extraction can be merged into a single API call by requesting a combined response object, reducing latency and cost compared to two sequential calls per image.

### Stage 4: Deduplication

See [Deduplication Strategy](#deduplication-strategy) below.

### Stage 5: Storage

**Input:** Validated, deduplication-checked transaction records.

**Process:** Records are persisted to a relational database with metadata fields (status, confidence score, source image path) in addition to the extracted transaction fields.

**Output:** Rows in the `transactions` table, scoped to the authenticated user's `user_id`. Full schema in `docs/SCHEMA.md`.

### Stage 6: Reporting

**Input:** Stored transaction records.

**Process:** Records are aggregated by date, source, and direction using Pandas. Summary metrics (total incoming, total outgoing, count of records pending review) are computed and displayed. Reports can be exported using openpyxl (Excel) or fpdf2 (PDF).

**Output:** A dashboard view and downloadable report file.

## Data Validation Strategy

All model output is validated against a Pydantic schema before being accepted:

```python
class Transaction(BaseModel):
    date: date
    amount: float
    transaction_type: str
    source: str
    counterparty: str | None
    reference_id: str | None
    raw_text: str
```

If the model returns output that does not conform to this schema (missing required fields, incorrect types, malformed dates), the record is not silently coerced or discarded. It is flagged for manual review, and the raw model response is retained for audit purposes.

## Deduplication Strategy

Deduplication is applied in three layers, in order of computational cost:

### Layer 1: Exact Match

Records are compared on the combination of date, amount, and reference ID (when present). An exact match on all three fields is treated as a certain duplicate.

### Layer 2: Fuzzy Match

When a reference ID is not available, records with matching date and amount are compared on counterparty name using string similarity (RapidFuzz). A similarity score above a defined threshold (default 85) is treated as a likely duplicate.

### Layer 3: Perceptual Image Hashing

Independent of extracted data, source images are compared using perceptual hashing (imagehash). This detects cases where the same screenshot was uploaded more than once, even before or regardless of successful data extraction, and can be used as an early filter to avoid redundant API calls.

Records flagged by any layer are marked with `status = "duplicate"` rather than removed, allowing the user to confirm or override the determination.

## Database Schema

```python
class Transaction(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    date: date
    amount: float
    transaction_type: str        # "incoming" or "outgoing"
    source: str                   # e.g. "BCA", "GoPay", "QRIS"
    counterparty: str | None
    reference_id: str | None
    image_path: str
    status: str = "unreviewed"    # unreviewed, confirmed, duplicate, rejected
    confidence_score: float
    uploaded_at: datetime = Field(default_factory=datetime.now)
```

Indexing recommendations for production use: an index on `(date, amount)` to accelerate fuzzy-match lookups, and an index on `reference_id` for exact-match lookups.

## Cost and Performance Considerations

- Each image may require one or two API calls (classification and extraction), which is the primary cost driver. Combining both into a single request reduces this to one call per image.
- Perceptual hashing is performed locally and is effectively free; running it before the API call avoids reprocessing images that are already known duplicates by pixel content.
- Preprocessing (resizing, compression) reduces both upload time and, for some providers, token-based image pricing.

## Known Limitations

- Extraction accuracy depends on image legibility; low-resolution or heavily cropped screenshots may produce incomplete or low-confidence results.
- Fuzzy matching thresholds are heuristic and may require tuning based on observed false-positive and false-negative rates.
- The system does not currently integrate with official banking or e-wallet APIs; all data originates from user-submitted screenshots.
- Multi-user access control and authentication are out of scope for the current version.

## Design Decisions and Trade-offs

| Decision | Alternative Considered | Reason for Choice |
|---|---|---|
| PostgreSQL (hosted on Neon) | SQLite | Multi-user application requires per-account data isolation and concurrent access; SQLite is single-writer and file-based, which does not fit a hosted, authenticated, multi-user product |
| Vision-language model for extraction | Traditional OCR plus rule-based parsing | Handles varied screenshot layouts across banks and wallets without per-source parsing rules; more robust to visual variation |
| FastAPI + Jinja2 + Tailwind + HTMX | Streamlit | Streamlit is optimized for internal tools and data apps, not authenticated, multi-user, mobile-friendly consumer interfaces; FastAPI keeps the authentication template, business logic, and rendering in one consistent stack. A Streamlit prototype was used early on to validate the screen flow before this decision |
| JWT (access + refresh tokens) | Session-based auth with server-side session store | Stateless and horizontally scalable without a shared session store; fits a small, free-tier deployment target |
| Flag-and-review for duplicates | Automatic deletion | Avoids irreversible data loss from false-positive duplicate detection |
| Render + Neon (separate app and database hosting) | Single all-in-one platform | Both offer free tiers without requiring a paid plan for a two-week hackathon timeline; decoupling app and database hosting avoids being blocked by a single platform's limits |