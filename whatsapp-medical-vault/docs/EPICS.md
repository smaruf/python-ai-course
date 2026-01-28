# WhatsApp Medical Report Vault – MVP Epics & Features

Complete breakdown of all 10 EPICs with implementation details, acceptance criteria, and technical specifications.

---

## EPIC 1: WhatsApp Business API Integration

**Goal:** Enable users to interact with the system entirely via WhatsApp.

### Features

#### 1.1 WhatsApp Business API Setup
- **Provider Selection**: Support for multiple providers
  - Meta Cloud API (recommended)
  - Twilio WhatsApp API
  - 360dialog
- **Configuration**:
  ```python
  WHATSAPP_PROVIDER = "meta"  # or "twilio" or "360dialog"
  WHATSAPP_API_TOKEN = "..."
  WHATSAPP_PHONE_NUMBER_ID = "..."
  WHATSAPP_BUSINESS_ACCOUNT_ID = "..."
  ```

#### 1.2 Webhook Endpoint
- **Endpoint**: `POST /webhook/whatsapp`
- **HTTP Method**: POST
- **Request Verification**: Signature-based validation
- **Response Time**: < 10 seconds (WhatsApp requirement)

**Implementation**:
```python
@app.post("/webhook/whatsapp")
async def webhook_handler(
    request: Request,
    background_tasks: BackgroundTasks
):
    # 1. Verify webhook signature
    # 2. Validate payload
    # 3. Acknowledge immediately (< 10s)
    # 4. Queue for async processing
    # 5. Return 200 OK
    pass
```

#### 1.3 Webhook Verification
- **GET Request**: For initial webhook setup
- **Verify Token**: Custom verification token
- **Challenge Response**: Echo challenge parameter

**Implementation**:
```python
@app.get("/webhook/whatsapp")
async def verify_webhook(
    mode: str = Query(..., alias="hub.mode"),
    token: str = Query(..., alias="hub.verify_token"),
    challenge: str = Query(..., alias="hub.challenge")
):
    if mode == "subscribe" and token == WEBHOOK_VERIFY_TOKEN:
        return int(challenge)
    raise HTTPException(status_code=403)
```

#### 1.4 Message Types Support

**Text Messages**:
```json
{
  "type": "text",
  "text": {
    "body": "LIST"
  }
}
```

**Image Uploads**:
```json
{
  "type": "image",
  "image": {
    "id": "media_id_here",
    "mime_type": "image/jpeg"
  }
}
```

**PDF Uploads**:
```json
{
  "type": "document",
  "document": {
    "id": "media_id_here",
    "mime_type": "application/pdf",
    "filename": "report.pdf"
  }
}
```

### Acceptance Criteria

✅ System reliably receives all message types
✅ Media IDs are captured correctly
✅ Webhook acknowledges within 10 seconds
✅ Failed messages are logged and retried
✅ Invalid signatures are rejected

### Technical Specifications

- **Framework**: FastAPI
- **Async Processing**: Celery/RQ workers
- **Queue**: Redis
- **Logging**: Structured JSON logs
- **Monitoring**: Prometheus metrics

---

## EPIC 2: Media Download & Validation

**Goal:** Securely fetch and validate uploaded medical documents.

### Features

#### 2.1 Media Fetching
- **WhatsApp Media API**: GET request to download media
- **Authentication**: Bearer token
- **Temporary Storage**: Secure temp directory during processing

**Implementation**:
```python
async def download_media(media_id: str) -> bytes:
    url = f"{WHATSAPP_API_URL}/{media_id}"
    headers = {"Authorization": f"Bearer {WHATSAPP_API_TOKEN}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        return response.content
```

#### 2.2 File Validation

**Format Validation**:
- Allowed: PDF, JPG, JPEG, PNG
- Detection: MIME type + magic bytes
- Libraries: `python-magic`, `filetype`

**Size Limits**:
- Images: Max 16 MB
- PDFs: Max 16 MB (WhatsApp limit)
- Configurable per file type

**Implementation**:
```python
def validate_file(file_data: bytes, mime_type: str) -> ValidationResult:
    # Check MIME type
    if mime_type not in ALLOWED_MIME_TYPES:
        return ValidationResult(valid=False, error="Invalid file type")
    
    # Verify magic bytes
    detected_type = filetype.guess(file_data)
    if detected_type is None or detected_type.mime != mime_type:
        return ValidationResult(valid=False, error="File type mismatch")
    
    # Check file size
    if len(file_data) > MAX_FILE_SIZE:
        return ValidationResult(valid=False, error="File too large")
    
    return ValidationResult(valid=True)
```

#### 2.3 Virus/Malware Scan (Optional)

**Options**:
1. **ClamAV** (open-source)
2. **VirusTotal API**
3. **AWS S3 Virus Scanning** (third-party)

**Configuration**:
```yaml
security:
  virus_scan:
    enabled: true
    provider: "clamav"  # or "virustotal"
    fail_on_error: false  # Continue if scan unavailable
```

**Implementation**:
```python
async def scan_file(file_data: bytes) -> ScanResult:
    if not ENABLE_VIRUS_SCAN:
        return ScanResult(clean=True, skipped=True)
    
    # ClamAV example
    cd = pyclamd.ClamdNetworkSocket(host=CLAMAV_HOST, port=CLAMAV_PORT)
    result = cd.scan_stream(file_data)
    
    if result is None:
        return ScanResult(clean=True)
    else:
        return ScanResult(clean=False, threat=result)
```

### Acceptance Criteria

✅ Invalid files rejected with user-friendly messages
✅ Valid files proceed to metadata collection
✅ No files publicly accessible during processing
✅ Malicious files blocked (if scanning enabled)
✅ Failed downloads logged and retried

### Error Messages

```
"❌ Invalid file format. Please send PDF, JPG, or PNG only."
"❌ File too large. Maximum size: 16 MB."
"⚠️ Could not download file. Please try again."
"❌ Security scan failed. Please contact support."
```

---

## EPIC 3: Conversational Metadata Collection (Stateful Flow)

**Goal:** Collect required metadata via multi-step WhatsApp conversation.

### Features

#### 3.1 Session Management

**Session State**:
```python
class SessionState(Enum):
    IDLE = "idle"
    AWAITING_MEDIA = "awaiting_media"
    AWAITING_DATE = "awaiting_date"
    AWAITING_HOSPITAL = "awaiting_hospital"
    AWAITING_REPORT_TYPE = "awaiting_report_type"
    CONFIRMING = "confirming"
    COMPLETE = "complete"
```

**Session Storage**:
- **Primary**: PostgreSQL (persistent)
- **Cache**: Redis (fast access)
- **TTL**: 30 minutes of inactivity

**Session Model**:
```python
class Session:
    id: UUID
    phone_number: str
    state: SessionState
    context_data: dict
    pending_media_id: Optional[str]
    temp_storage_path: Optional[str]
    started_at: datetime
    last_activity: datetime
    expires_at: datetime
```

#### 3.2 Multi-Step Flow

**Flow Definition**:
```python
CONVERSATION_FLOW = {
    "media_received": {
        "next_state": "awaiting_date",
        "prompt": "📅 When was this report created? (DD/MM/YYYY)",
        "validator": validate_date_input
    },
    "date_received": {
        "next_state": "awaiting_hospital",
        "prompt": "🏥 Which hospital issued this report?",
        "validator": validate_hospital_input
    },
    "hospital_received": {
        "next_state": "awaiting_report_type",
        "prompt": "📋 What type of report is this?\n\nExamples:\n• Blood Test\n• MRI Scan\n• X-Ray\n• Prescription",
        "validator": validate_report_type_input
    },
    "report_type_received": {
        "next_state": "confirming",
        "prompt": "✅ Please confirm:\n📅 Date: {date}\n🏥 Hospital: {hospital}\n📋 Type: {report_type}\n\nType YES to save or CANCEL to restart.",
        "validator": validate_confirmation
    }
}
```

#### 3.3 Input Validation & Re-prompting

**Date Validation**:
```python
def validate_date_input(text: str) -> ValidationResult:
    # Try multiple formats
    formats = ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"]
    
    for fmt in formats:
        try:
            date = datetime.strptime(text, fmt)
            if date > datetime.now():
                return ValidationResult(
                    valid=False,
                    error="Date cannot be in the future."
                )
            return ValidationResult(valid=True, value=date)
        except ValueError:
            continue
    
    return ValidationResult(
        valid=False,
        error="Invalid date format. Please use DD/MM/YYYY."
    )
```

**Hospital Validation**:
```python
def validate_hospital_input(text: str) -> ValidationResult:
    if len(text.strip()) < 2:
        return ValidationResult(
            valid=False,
            error="Hospital name too short. Please try again."
        )
    
    if len(text) > 255:
        return ValidationResult(
            valid=False,
            error="Hospital name too long. Please use a shorter name."
        )
    
    return ValidationResult(valid=True, value=text.strip())
```

**Report Type Validation**:
```python
COMMON_REPORT_TYPES = [
    "Blood Test", "MRI Scan", "CT Scan", "X-Ray",
    "Ultrasound", "ECG", "Prescription", "Lab Report",
    "Vaccination Record", "Discharge Summary"
]

def validate_report_type_input(text: str) -> ValidationResult:
    # Allow custom types, but suggest common ones
    if len(text.strip()) < 2:
        return ValidationResult(
            valid=False,
            error="Report type too short. Please try again."
        )
    
    return ValidationResult(valid=True, value=text.strip())
```

#### 3.4 Cancel / Restart Support

**Commands**:
- `CANCEL` - Cancel current operation
- `RESTART` - Start over
- `HELP` - Show help

**Implementation**:
```python
async def handle_cancel(session: Session) -> None:
    # Clean up temporary files
    if session.temp_storage_path:
        await cleanup_temp_file(session.temp_storage_path)
    
    # Reset session
    session.state = SessionState.IDLE
    session.context_data = {}
    session.pending_media_id = None
    await save_session(session)
    
    await send_message(
        session.phone_number,
        "❌ Operation cancelled. Send a new file to start over."
    )
```

#### 3.5 Timeout Handling

**Configuration**:
```yaml
session:
  timeout_minutes: 30
  reminder_minutes: 25
```

**Implementation**:
```python
# Celery periodic task
@celery.task
def check_expired_sessions():
    now = datetime.utcnow()
    expired_sessions = Session.query.filter(
        Session.expires_at < now,
        Session.state != SessionState.COMPLETE
    ).all()
    
    for session in expired_sessions:
        cleanup_expired_session(session)
```

### Acceptance Criteria

✅ Each user completes flow independently (no interference)
✅ Incomplete sessions don't corrupt data
✅ Users can restart/cancel at any point
✅ Invalid inputs trigger helpful re-prompts
✅ Sessions expire after 30 minutes of inactivity
✅ Expired sessions are cleaned up automatically

### User Experience

```
User: [Uploads PDF]
Bot: "📄 File received! Let's add some details."
     "📅 When was this report created? (DD/MM/YYYY)"

User: "25/12/2025"
Bot: "✅ Date saved: 25 December 2025"
     "🏥 Which hospital issued this report?"

User: "City General Hospital"
Bot: "✅ Hospital saved"
     "📋 What type of report is this?"

User: "Blood Test"
Bot: "✅ Please confirm:
     📅 Date: 25/12/2025
     🏥 Hospital: City General Hospital
     📋 Type: Blood Test
     
     Type YES to save or CANCEL to restart."

User: "YES"
Bot: "✅ Report saved successfully!
     
     Commands:
     • LIST - View all reports
     • LATEST - Get latest report
     • HELP - Show help"
```

---

## EPIC 4: Secure File Storage

**Goal:** Store medical reports securely and reliably.

### Features

#### 4.1 Cloud Storage Integration

**Supported Providers**:
1. **AWS S3**
2. **DigitalOcean Spaces**
3. **Google Cloud Storage** (future)

**Configuration**:
```python
STORAGE_PROVIDER = "s3"  # or "spaces"
AWS_ACCESS_KEY_ID = "..."
AWS_SECRET_ACCESS_KEY = "..."
AWS_S3_BUCKET = "medical-vault-prod"
AWS_REGION = "us-east-1"
```

#### 4.2 Private Bucket Configuration

**S3 Bucket Policy** (Block all public access):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::medical-vault-prod/*",
      "Condition": {
        "StringNotEquals": {
          "aws:PrincipalAccount": "YOUR_ACCOUNT_ID"
        }
      }
    }
  ]
}
```

**Bucket Settings**:
- ✅ Block public access: ON
- ✅ Versioning: Enabled
- ✅ Server-side encryption: AES-256 or KMS
- ✅ Lifecycle policies: Optional archival
- ✅ Access logging: Enabled

#### 4.3 Server-Side Encryption

**AWS S3 Encryption**:
```python
import boto3

s3_client = boto3.client('s3')

def upload_encrypted_file(file_data: bytes, key: str):
    s3_client.put_object(
        Bucket=AWS_S3_BUCKET,
        Key=key,
        Body=file_data,
        ServerSideEncryption='AES256',  # or 'aws:kms'
        StorageClass='STANDARD_IA',  # Infrequent Access
        ContentType=mime_type,
        Metadata={
            'uploaded_by': 'whatsapp_vault',
            'upload_timestamp': str(datetime.utcnow())
        }
    )
```

#### 4.4 Structured Object Naming

**Naming Convention**:
```
/users/{phone_number}/reports/{year}/{uuid}.{ext}

Example:
/users/+1234567890/reports/2025/a1b2c3d4-e5f6-7890-abcd-ef1234567890.pdf
```

**Benefits**:
- Easy organization by user
- Year-based partitioning
- UUID prevents name conflicts
- Supports multiple file types

**Implementation**:
```python
def generate_storage_key(
    phone_number: str,
    report_date: datetime,
    file_extension: str
) -> str:
    # Sanitize phone number (remove special chars)
    clean_phone = re.sub(r'[^0-9+]', '', phone_number)
    
    # Generate UUID
    file_uuid = str(uuid.uuid4())
    
    # Build key
    year = report_date.year
    key = f"users/{clean_phone}/reports/{year}/{file_uuid}.{file_extension}"
    
    return key
```

#### 4.5 Upload Confirmation

**Successful Upload**:
```
✅ Report saved successfully!

📄 Blood Test Report
📅 25/12/2025
🏥 City General Hospital
🆔 Report ID: 1

Type HELP for available commands.
```

**Failed Upload**:
```
❌ Upload failed. Please try again.

If the problem persists, contact support.
```

### Acceptance Criteria

✅ Files encrypted at rest (AES-256 or KMS)
✅ Files not publicly accessible
✅ Upload failures handled gracefully with retries
✅ Storage keys follow structured naming
✅ Users receive confirmation after successful upload
✅ Failed uploads don't leave orphaned data

### Security Checklist

- ✅ No public bucket access
- ✅ Encryption enabled
- ✅ IAM roles (least privilege)
- ✅ Access logging enabled
- ✅ Versioning enabled (recovery)
- ✅ Lifecycle policies (cost optimization)

---

## EPIC 5: Metadata Persistence & Database Design

**Goal:** Store searchable metadata linked to each document.

### Features

#### 5.1 Database Schema

See [data-model.puml](diagrams/data-model.puml) for complete schema.

**Core Tables**:

1. **users**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    last_active TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'active',
    INDEX idx_phone (phone_number)
);
```

2. **reports**
```sql
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    report_date DATE NOT NULL,
    hospital_name VARCHAR(255) NOT NULL,
    report_type VARCHAR(100) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(10) NOT NULL,
    file_size BIGINT NOT NULL,
    storage_key VARCHAR(500) UNIQUE NOT NULL,
    storage_url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_report_date (report_date),
    INDEX idx_report_type (report_type),
    INDEX idx_created_at (created_at),
    INDEX idx_deleted_at (deleted_at)
);
```

3. **sessions**
```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    phone_number VARCHAR(20) NOT NULL,
    state VARCHAR(50) NOT NULL,
    current_step VARCHAR(50),
    context_data JSONB DEFAULT '{}',
    pending_media_id VARCHAR(255),
    temp_storage_path VARCHAR(500),
    started_at TIMESTAMP DEFAULT NOW(),
    last_activity TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    INDEX idx_phone (phone_number),
    INDEX idx_user_id (user_id),
    INDEX idx_state (state),
    INDEX idx_expires_at (expires_at)
);
```

4. **audit_logs**
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    report_id UUID REFERENCES reports(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    details JSONB DEFAULT '{}',
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_id (user_id),
    INDEX idx_report_id (report_id),
    INDEX idx_action (action),
    INDEX idx_created_at (created_at)
);
```

#### 5.2 Indexing Strategy

**Fast Retrieval Indexes**:
- User phone number (unique index)
- Report date (range queries)
- Report type (filtering)
- Created timestamp (sorting)
- Deleted at (soft delete queries)

**Composite Indexes** (for common queries):
```sql
CREATE INDEX idx_user_date ON reports(user_id, report_date DESC);
CREATE INDEX idx_user_type ON reports(user_id, report_type);
CREATE INDEX idx_user_created ON reports(user_id, created_at DESC);
```

#### 5.3 Soft Delete Support

**Implementation**:
```python
def soft_delete_report(report_id: UUID, user_id: UUID):
    report = Report.query.filter_by(
        id=report_id,
        user_id=user_id,
        deleted_at=None
    ).first()
    
    if not report:
        raise NotFoundError("Report not found")
    
    report.deleted_at = datetime.utcnow()
    db.session.commit()
    
    # Audit log
    log_action(
        user_id=user_id,
        action="delete",
        resource_type="report",
        resource_id=report_id
    )
```

**Query Active Reports**:
```python
active_reports = Report.query.filter(
    Report.user_id == user_id,
    Report.deleted_at.is_(None)
).order_by(Report.created_at.desc()).all()
```

#### 5.4 Data Consistency

**Transaction Handling**:
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

async def save_report_with_metadata(
    file_data: bytes,
    metadata: ReportMetadata,
    user_id: UUID
):
    async with db.begin():  # Transaction
        # 1. Upload to S3
        storage_key = await upload_to_s3(file_data, metadata)
        
        # 2. Save metadata to database
        report = Report(
            user_id=user_id,
            report_date=metadata.date,
            hospital_name=metadata.hospital,
            report_type=metadata.report_type,
            storage_key=storage_key,
            file_size=len(file_data),
            file_type=metadata.file_extension
        )
        db.session.add(report)
        
        # 3. Update session
        session = await get_session(metadata.phone_number)
        session.state = SessionState.COMPLETE
        
        # 4. Audit log
        audit_log = AuditLog(
            user_id=user_id,
            report_id=report.id,
            action="upload",
            resource_type="report"
        )
        db.session.add(audit_log)
        
        # Commit all or rollback all
        await db.commit()
```

### Acceptance Criteria

✅ Metadata and file references stay in sync (transactions)
✅ No orphaned records
✅ Queries return results within acceptable time (< 100ms)
✅ Soft delete preserves data for recovery
✅ Indexes optimize common query patterns

---

## EPIC 6: Report Retrieval via WhatsApp Commands

**Goal:** Allow users to retrieve past medical reports easily.

### Features

#### 6.1 Command Parser

**Supported Commands**:
```python
COMMANDS = {
    "LIST": list_reports,
    "LIST {year}": list_reports_by_year,
    "GET {id}": get_report_by_id,
    "LATEST": get_latest_report,
    "HELP": show_help,
    "CANCEL": cancel_operation
}
```

**Parser Implementation**:
```python
import re

def parse_command(text: str) -> Command:
    text = text.strip().upper()
    
    # LIST command
    if text == "LIST":
        return Command(action="list_all")
    
    # LIST <year>
    match = re.match(r"LIST\s+(\d{4})", text)
    if match:
        year = int(match.group(1))
        return Command(action="list_by_year", params={"year": year})
    
    # GET <id>
    match = re.match(r"GET\s+(\d+)", text)
    if match:
        report_id = int(match.group(1))
        return Command(action="get_report", params={"id": report_id})
    
    # LATEST
    if text == "LATEST":
        return Command(action="get_latest")
    
    # HELP
    if text == "HELP":
        return Command(action="help")
    
    # Unknown
    return Command(action="unknown")
```

#### 6.2 LIST Command

**Implementation**:
```python
async def list_reports(user_id: UUID, page: int = 1, per_page: int = 10):
    reports = Report.query.filter(
        Report.user_id == user_id,
        Report.deleted_at.is_(None)
    ).order_by(
        Report.created_at.desc()
    ).paginate(page=page, per_page=per_page)
    
    if not reports.items:
        return "📋 No reports found.\n\nUpload a file to get started!"
    
    message = f"📋 Your Reports (Page {page}/{reports.pages}):\n\n"
    
    for idx, report in enumerate(reports.items, start=1):
        message += (
            f"{idx}. {report.report_type}\n"
            f"   📅 {report.report_date.strftime('%d/%m/%Y')}\n"
            f"   🏥 {report.hospital_name}\n"
            f"   🆔 ID: {report.id}\n\n"
        )
    
    if reports.has_next:
        message += f"\nType 'LIST {page + 1}' for more results."
    
    return message
```

#### 6.3 LIST <year> Command

**Implementation**:
```python
async def list_reports_by_year(user_id: UUID, year: int):
    reports = Report.query.filter(
        Report.user_id == user_id,
        extract('year', Report.report_date) == year,
        Report.deleted_at.is_(None)
    ).order_by(Report.report_date.desc()).all()
    
    if not reports:
        return f"📋 No reports found for {year}."
    
    message = f"📋 Your Reports from {year}:\n\n"
    
    for idx, report in enumerate(reports, start=1):
        message += (
            f"{idx}. {report.report_type}\n"
            f"   📅 {report.report_date.strftime('%d/%m/%Y')}\n"
            f"   🏥 {report.hospital_name}\n\n"
        )
    
    return message
```

#### 6.4 GET <id> Command

**Implementation**:
```python
async def get_report_by_id(user_id: UUID, report_id: UUID):
    # Verify ownership
    report = Report.query.filter_by(
        id=report_id,
        user_id=user_id,
        deleted_at=None
    ).first()
    
    if not report:
        return "❌ Report not found or access denied."
    
    # Generate signed URL (expires in 1 hour)
    signed_url = generate_signed_url(
        report.storage_key,
        expires_in=3600
    )
    
    # Download file from S3
    file_data = await download_from_s3(report.storage_key)
    
    # Upload to WhatsApp
    media_id = await upload_to_whatsapp(file_data, report.file_type)
    
    # Send with metadata
    caption = (
        f"📄 {report.report_type}\n"
        f"📅 {report.report_date.strftime('%d %B %Y')}\n"
        f"🏥 {report.hospital_name}"
    )
    
    await send_media_message(
        phone_number=get_phone_number(user_id),
        media_id=media_id,
        caption=caption
    )
    
    # Audit log
    log_access(user_id, report_id, "retrieve")
    
    return "✅ Report sent!"
```

#### 6.5 LATEST Command

**Implementation**:
```python
async def get_latest_report(user_id: UUID):
    report = Report.query.filter(
        Report.user_id == user_id,
        Report.deleted_at.is_(None)
    ).order_by(Report.created_at.desc()).first()
    
    if not report:
        return "📋 No reports found."
    
    # Same logic as GET command
    return await get_report_by_id(user_id, report.id)
```

#### 6.6 Pagination

**Implementation**:
```python
MAX_RESULTS_PER_PAGE = 10

def paginate_results(results: List, page: int = 1):
    start = (page - 1) * MAX_RESULTS_PER_PAGE
    end = start + MAX_RESULTS_PER_PAGE
    
    paginated = results[start:end]
    has_more = len(results) > end
    
    return {
        "items": paginated,
        "page": page,
        "total_pages": (len(results) + MAX_RESULTS_PER_PAGE - 1) // MAX_RESULTS_PER_PAGE,
        "has_more": has_more
    }
```

### Acceptance Criteria

✅ Users can retrieve only their own files
✅ Commands respond correctly and quickly (< 2s)
✅ Large result sets are paginated
✅ Invalid commands show helpful error messages
✅ Access is logged in audit trail

---

## EPIC 7: Privacy, Security & Compliance (MVP Level)

**Goal:** Protect sensitive medical data.

### Features

#### 7.1 Phone-Based Access Control

**Implementation**:
```python
def authorize_access(phone_number: str, report_id: UUID) -> bool:
    user = User.query.filter_by(phone_number=phone_number).first()
    if not user:
        return False
    
    report = Report.query.filter_by(
        id=report_id,
        user_id=user.id
    ).first()
    
    return report is not None
```

#### 7.2 Logging Without Sensitive Data

**Bad (Don't Do)**:
```python
logger.info(f"User {phone_number} uploaded report about diabetes")
```

**Good (Do This)**:
```python
logger.info(
    "User uploaded report",
    extra={
        "user_id": hash_phone_number(phone_number),
        "report_type": "REDACTED",
        "action": "upload"
    }
)
```

#### 7.3 Phone Number Masking

**Implementation**:
```python
def mask_phone_number(phone: str) -> str:
    if len(phone) < 4:
        return "****"
    return f"****{phone[-4:]}"

# In logs
logger.info(f"Request from {mask_phone_number(phone_number)}")
```

#### 7.4 Environment Variables

**Required Variables**:
```bash
# .env file (NEVER commit to git)
SECRET_KEY=...
DATABASE_URL=...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
WHATSAPP_API_TOKEN=...
```

**Loading**:
```python
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY not set")
```

#### 7.5 Audit Trail

**Log All Actions**:
- Upload
- Retrieve
- Delete
- List
- Failed access attempts

**Implementation**:
```python
def log_action(
    user_id: UUID,
    action: str,
    resource_type: str,
    resource_id: Optional[UUID] = None,
    details: dict = None
):
    audit = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details or {},
        created_at=datetime.utcnow()
    )
    db.session.add(audit)
    db.session.commit()
```

### Acceptance Criteria

✅ Unauthorized access impossible
✅ Logs contain no medical data or full phone numbers
✅ Storage access restricted by IAM policy
✅ All secrets in environment variables
✅ Complete audit trail for compliance

---

## EPIC 8: Error Handling & User Experience

**Goal:** Ensure smooth WhatsApp user experience.

### Features

#### 8.1 Friendly Error Messages

**Instead of**:
```
Error 500: Internal Server Error
```

**Show**:
```
❌ Something went wrong. Please try again.

If the problem persists, contact support.
```

#### 8.2 Retry Prompts

**Example**:
```
❌ Invalid date format.

Please enter the date as DD/MM/YYYY

Example: 25/12/2025
```

#### 8.3 Success Confirmations

**After Upload**:
```
✅ Report saved successfully!

📄 Blood Test Report
📅 25/12/2025
🏥 City General Hospital

Type HELP for available commands.
```

#### 8.4 HELP Command

**Implementation**:
```
📖 Available Commands:

📋 LIST - View all your reports
📋 LIST 2025 - View reports from 2025
📄 GET 1 - Download report #1
📄 LATEST - Get your latest report
❌ CANCEL - Cancel current operation
📖 HELP - Show this message

To upload a report, just send a PDF or image!
```

#### 8.5 Unsupported Messages

**For voice messages, videos, etc.**:
```
❓ I can only process text messages, images, and PDFs.

Type HELP to see available commands.
```

### Acceptance Criteria

✅ Users always know what to do next
✅ Errors never expose system internals
✅ System recovers from partial failures
✅ Clear visual indicators (✅, ❌, 📄, etc.)

---

## EPIC 9: Observability & Operations

**Goal:** Enable basic monitoring and troubleshooting.

### Features

#### 9.1 Request Logging

**Structured Logging**:
```python
import structlog

logger = structlog.get_logger()

logger.info(
    "webhook_received",
    phone_number=mask_phone_number(phone),
    message_type=msg_type,
    timestamp=datetime.utcnow().isoformat()
)
```

#### 9.2 Error Tracking

**Sentry Integration**:
```python
import sentry_sdk

sentry_sdk.init(
    dsn=SENTRY_DSN,
    environment=ENVIRONMENT,
    traces_sample_rate=0.1
)

# Automatic error capture
try:
    process_message(msg)
except Exception as e:
    sentry_sdk.capture_exception(e)
    raise
```

#### 9.3 Health Checks

**Endpoint**:
```python
@app.get("/health")
async def health_check():
    checks = {
        "api": "ok",
        "database": await check_database(),
        "redis": await check_redis(),
        "s3": await check_s3()
    }
    
    all_ok = all(v == "ok" for v in checks.values())
    
    return {
        "status": "healthy" if all_ok else "degraded",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }
```

#### 9.4 Metrics

**Prometheus Metrics**:
```python
from prometheus_client import Counter, Histogram

# Counters
messages_received = Counter(
    'whatsapp_messages_received_total',
    'Total messages received',
    ['message_type']
)

files_uploaded = Counter(
    'files_uploaded_total',
    'Total files uploaded',
    ['file_type', 'status']
)

# Histograms
processing_time = Histogram(
    'message_processing_seconds',
    'Time to process message'
)

# Usage
messages_received.labels(message_type='text').inc()

with processing_time.time():
    process_message(msg)
```

### Acceptance Criteria

✅ System health visible via /health endpoint
✅ Failures diagnosed quickly via logs
✅ Metrics tracked for performance monitoring
✅ Errors sent to Sentry for investigation

---

## EPIC 10: Deployment & Handover

**Goal:** Deliver usable, maintainable MVP.

### Features

#### 10.1 Environment Setup

**Environments**:
- Development (local)
- Staging (pre-production)
- Production

**Configuration Files**:
```yaml
# configs/production.yaml
database:
  pool_size: 20
  max_overflow: 40

session:
  timeout_minutes: 30

storage:
  provider: s3
  bucket: medical-vault-prod

whatsapp:
  provider: meta
  webhook_timeout: 10
```

#### 10.2 Deployment Scripts

**Docker Compose**:
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - postgres
      - redis
  
  worker:
    build: .
    command: celery -A src.whatsapp_vault.workers worker
    depends_on:
      - redis
  
  postgres:
    image: postgres:15
    volumes:
      - pgdata:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
```

#### 10.3 Documentation

**Included**:
- README.md (overview)
- ARCHITECTURE.md (design)
- API.md (endpoints)
- DEPLOYMENT.md (ops guide)
- SECURITY.md (security)
- EPICS.md (features)

#### 10.4 Handover Walkthrough

**Checklist**:
- ✅ Architecture explained
- ✅ Code walkthrough
- ✅ Deployment demonstrated
- ✅ Monitoring shown
- ✅ Common issues documented
- ✅ Contact information provided

### Acceptance Criteria

✅ Client can operate system independently
✅ Clear documentation exists
✅ Deployment is automated
✅ Troubleshooting guide available

---

## Summary

All 10 EPICs provide a comprehensive, production-ready WhatsApp Medical Report Vault system with:

- ✅ Modern architecture (webhook/pub-sub, push-pull)
- ✅ Secure storage (encryption, access control)
- ✅ Great UX (conversational, friendly errors)
- ✅ Observability (logging, metrics, health checks)
- ✅ Compliance-ready (audit trails, privacy)

**Next Steps**: Implementation phase following this architecture.
