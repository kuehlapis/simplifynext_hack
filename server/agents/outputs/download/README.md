# Frontend Package Documentation

This directory contains all the generated files from the AI agent pipeline for easy access by your frontend application.

## Main Files

### 1. `frontend_package.json` (Recommended)
This is the **main file** your frontend should consume. It contains all the necessary data in a single, structured JSON file:

- **Metadata**: Document title, date, generation timestamp
- **Risk Summary**: High/medium/low risk counts
- **Flagged Clauses**: All problematic clauses with details
- **Artifacts**: Consolidated content from all generated documents
- **Recommendations**: Top actions and priority issues
- **Document Analysis**: Risk distribution and category breakdown

### 2. `dashboard.json`
Traditional dashboard format with artifact links pointing to individual files.

### 3. Individual Artifact Files
- `negotiation_rider_*.json` - Proposed changes to unfair clauses
- `tenant_email_*.json` - Email template for tenant notification
- `planner-agent.json` - Task list and recommendations
- `planner_event.ics` - Calendar event for agreement review

## Frontend Integration

### Option 1: Use frontend_package.json (Recommended)
```javascript
// Fetch the comprehensive package
fetch('/download/frontend_package.json')
  .then(response => response.json())
  .then(data => {
    // Access all data from one file
    const riskSummary = data.risk_summary;
    const flaggedClauses = data.flagged_clauses;
    const artifacts = data.artifacts;
    const recommendations = data.recommendations;
  });
```

### Option 2: Use dashboard.json + individual files
```javascript
// Fetch dashboard first
fetch('/download/dashboard.json')
  .then(response => response.json())
  .then(dashboard => {
    // Then fetch individual artifacts as needed
    dashboard.artifacts.forEach(artifact => {
      fetch(`/download/${artifact.url}`)
        .then(response => response.json())
        .then(artifactData => {
          // Process individual artifact
        });
    });
  });
```

## File Structure

```
download/
├── frontend_package.json     # 🎯 MAIN FILE - Use this!
├── dashboard.json            # Traditional dashboard format
├── download_index.json       # File listing with metadata
├── negotiation_rider_*.json  # Negotiation recommendations
├── tenant_email_*.json       # Email templates
├── planner-agent.json        # Task lists
├── planner_event.ics         # Calendar events
└── README.md                 # This file
```

## Data Schema

The `frontend_package.json` follows this structure:

```json
{
  "metadata": {
    "title": "Document Title",
    "date": "Document Date",
    "generated_at": "ISO Timestamp",
    "document_id": "Unique ID",
    "version": "1.0",
    "package_type": "frontend_ready"
  },
  "risk_summary": {
    "high": 25,
    "medium": 1,
    "ok": 0,
    "total": 26
  },
  "flagged_clauses": [...],
  "categories": [...],
  "artifacts": {
    "negotiation_rider": {...},
    "tenant_email": {...},
    "planner_summary": {...},
    "calendar_event": {...},
    "agreement_summary": {...}
  },
  "recommendations": {
    "top_actions": [...],
    "priority_issues": [...]
  },
  "document_analysis": {
    "total_clauses": 30,
    "risk_distribution": {...},
    "category_breakdown": {...}
  }
}
```

## Benefits of Using frontend_package.json

1. **Single API Call**: Get all data in one request
2. **No File Dependencies**: All content is embedded
3. **Consistent Structure**: Predictable data format
4. **Easy Caching**: Cache one file instead of multiple
5. **Offline Support**: All data available after initial load
6. **Reduced Network Overhead**: Fewer HTTP requests

## Updating the Package

The package is automatically regenerated each time the packager agent runs. Simply run:

```bash
cd server
python agents/packager.py
```

This will update both the main outputs and the download directory with fresh data.

## Support

If you encounter any issues with the package format or need additional data fields, please check the packager agent code in `server/agents/packager.py`.
