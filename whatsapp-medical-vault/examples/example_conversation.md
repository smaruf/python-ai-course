# Example WhatsApp Conversation Flow

This document shows an example conversation flow for uploading a medical report.

## Upload Flow

### Step 1: Upload Document

**User:** [Sends a PDF file via WhatsApp]

**Bot:**
```
📄 File received! Let's add some details.

📅 When was this report created? (DD/MM/YYYY)
```

### Step 2: Provide Report Date

**User:** `25/12/2025`

**Bot:**
```
✅ Date saved: 25 December 2025

🏥 Which hospital issued this report?
```

### Step 3: Provide Hospital Name

**User:** `City General Hospital`

**Bot:**
```
✅ Hospital saved

📋 What type of report is this?

Examples:
• Blood Test
• MRI Scan
• X-Ray
• Prescription
```

### Step 4: Provide Report Type

**User:** `Blood Test`

**Bot:**
```
✅ Please confirm:

📅 Date: 25/12/2025
🏥 Hospital: City General Hospital
📋 Type: Blood Test

Type YES to save or CANCEL to restart.
```

### Step 5: Confirm

**User:** `YES`

**Bot:**
```
✅ Report saved successfully!

📄 Blood Test Report
📅 25/12/2025
🏥 City General Hospital
🆔 Report ID: 1

Commands:
• LIST - View all reports
• LATEST - Get latest report
• HELP - Show help
```

## Retrieval Flow

### LIST Command

**User:** `LIST`

**Bot:**
```
📋 Your Reports (Page 1/1):

1. Blood Test
   📅 25/12/2025
   🏥 City General Hospital
   🆔 ID: 1

2. MRI Scan
   📅 20/11/2025
   🏥 Central Medical Center
   🆔 ID: 2

3. X-Ray
   📅 15/10/2025
   🏥 City General Hospital
   🆔 ID: 3

Type 'GET <ID>' to download a report.
```

### GET Command

**User:** `GET 1`

**Bot:**
```
📄 Blood Test Report
📅 25 December 2025
🏥 City General Hospital

[PDF Document Attached]
```

### LATEST Command

**User:** `LATEST`

**Bot:**
```
📄 Your latest report:

Blood Test Report
📅 25/12/2025
🏥 City General Hospital

[PDF Document Attached]
```

## Error Handling

### Invalid Date Format

**User:** `25-12-2025` (wrong format)

**Bot:**
```
❌ Invalid date format.

Please enter the date as DD/MM/YYYY

Example: 25/12/2025
```

### Invalid File Type

**User:** [Sends a video file]

**Bot:**
```
❌ Invalid file format. Please send PDF, JPG, or PNG only.

Allowed formats:
📄 PDF documents
🖼️ JPG/PNG images
```

### Cancel Operation

**User:** `CANCEL`

**Bot:**
```
❌ Operation cancelled. Send a new file to start over.
```

## Help Command

**User:** `HELP`

**Bot:**
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
