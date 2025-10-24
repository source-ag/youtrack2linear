# YouTrack to Linear Migration Tool

A simple Python tool to export issues from YouTrack and prepare them for import into Linear using Linear's official import tool.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Purpose

This tool helps you migrate from YouTrack to Linear as your issue tracking system by:
1. **Exporting issues** from YouTrack using their REST API
2. **Transforming data** to Linear-compatible format
3. **Preparing files** for Linear's official import tool

## Quick Start

### 1. Setup

```bash
# Clone and setup
git clone <repository-url>
cd youtrack2linear

# Install Python dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install Linear's official import tool
npm install --global @linear/import
```

### 2. Configuration

Create a `.env` file with your credentials:

```env
# YouTrack Configuration
YOUTRACK_URL=https://your-instance.myjetbrains.com/youtrack
YOUTRACK_TOKEN=your_youtrack_permanent_token
YOUTRACK_PROJECT_KEY=PROJECT_KEY

# Linear Configuration  
LINEAR_TEAM_KEY=your_linear_team_key
```

### 3. Export and Transform

```bash
# Export issues from YouTrack
python migrate.py export --query "project: {PROJECT_KEY}"

# Transform to Linear CSV format
python transformer.py
```

### 4. Import to Linear

1. Go to Linear → Settings → Import Export
2. Upload `output/linear_issues.csv`
3. Map columns: Title → Title, Description → Description
4. Import!

## Files Created

- `output/youtrack_issues.json` - Raw export from YouTrack
- `output/linear_issues.csv` - CSV for Linear import (title and description only)

## Commands

```bash
# Test connections
python migrate.py test-connections

# Export from YouTrack
python migrate.py export --query "project: {PROJECT_KEY}"

# Transform to Linear CSV format
python transformer.py
```

## Getting API Keys

### YouTrack Token
1. Go to YouTrack → Profile → Authentication
2. Create a "Permanent Token"
3. Copy the token

### Linear API Key
1. Go to Linear → Settings → Account → Security
2. Create a new API key
3. Copy the key

## Data Mapping

The tool automatically maps YouTrack fields to Linear format:

| YouTrack | Linear | Notes |
|----------|--------|-------|
| `summary` | `title` | Issue title |
| `description` | `description` | Converts wiki markup to Markdown |
| `idReadable` | `identifier` | Issue ID (P-1234) |
| `created` | `createdAt` | ISO timestamp |
| `updated` | `updatedAt` | ISO timestamp |
| `assignee` | `assigneeId` | User email |
| `reporter` | `creatorId` | User email |
| `tags` | `labels` | Converted to Linear labels |

## Query Examples

```bash
# All issues in a project
python migrate.py export --query "project: {PROJECT_KEY}"

# Open issues only
python migrate.py export --query "project: {PROJECT_KEY} State: Open"

# Issues from last month
python migrate.py export --query "project: {PROJECT_KEY} created: -1M .. today"

# High priority issues
python migrate.py export --query "project: {PROJECT_KEY} Priority: Major"
```

## Troubleshooting

### YouTrack Connection Issues
- Verify your YouTrack URL is correct
- Check that your API token has sufficient permissions
- Ensure the YouTrack instance is accessible

### Linear Import Issues
- Make sure you have the correct Linear API key
- Verify your team key is correct
- Check that users exist in Linear (for assignee mapping)

## Why This Approach?

This tool uses **Linear's official import tool** (`@linear/import`) because:
- ✅ **Official support** from Linear team
- ✅ **Robust error handling** and validation
- ✅ **User mapping** and conflict resolution
- ✅ **Preview and review** before import
- ✅ **Rollback capabilities** if needed

## License

MIT License - see LICENSE file for details.