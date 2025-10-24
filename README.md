# YouTrack to Linear Migration Tool

A simple Python tool to export issues from YouTrack and prepare them for import into Linear using CSV format.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Purpose

This tool helps you migrate from YouTrack to Linear as your issue tracking system by:
1. **Exporting issues** from YouTrack using their REST API
2. **Transforming data** to Linear-compatible CSV format
3. **Preparing CSV files** for Linear's web import interface

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
```

### 2. Configuration

Create a `.env` file with your credentials:

```env
# YouTrack Configuration
YOUTRACK_URL=https://your-instance.myjetbrains.com/youtrack
YOUTRACK_TOKEN=your_youtrack_permanent_token
YOUTRACK_PROJECT_KEY=PROJECT_KEY

# Linear Configuration (optional - not needed for CSV import)
# LINEAR_TEAM_KEY=your_linear_team_key
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

### Linear Import
No API key needed! The CSV import uses Linear's web interface:
1. Go to Linear → Settings → Import Export
2. Upload your CSV file
3. Map columns and import

## Data Mapping

The tool creates a simple CSV with all required columns for Linear import, but only populates:

| YouTrack | Linear CSV | Notes |
|----------|-------------|-------|
| `summary` | `Title` | Issue title |
| `description` | `Description` | Issue description |
| *(empty)* | `Created At` | Empty for simple import |
| *(empty)* | `Updated At` | Empty for simple import |
| *(empty)* | `Identifier` | Empty for simple import |
| *(empty)* | `Creator Email` | Empty for simple import |
| *(empty)* | `Assignee Email` | Empty for simple import |
| *(empty)* | `Priority` | Empty for simple import |
| *(empty)* | `State` | Empty for simple import |
| *(empty)* | `Labels` | Empty for simple import |

**Note**: This approach focuses on importing just the essential issue information (title and description) while maintaining compatibility with Linear's import format.

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
- Make sure your CSV file has the correct format
- Verify that the Title and Description columns are properly mapped
- Check that the CSV file is not too large (Linear has import limits)

## Why This Approach?

This tool uses **Linear's web import interface** because:
- ✅ **Simple and reliable** - No CLI tools or complex setup required
- ✅ **Web-based interface** - Easy to use and accessible from anywhere
- ✅ **Visual mapping** - See exactly how your data will be imported
- ✅ **Error handling** - Linear shows import errors and warnings
- ✅ **Flexible** - You can choose which columns to import and how to map them

## License

MIT License - see LICENSE file for details.