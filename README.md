# YouTrack to Linear Migration Tool

A simple Python tool to export issues from YouTrack and prepare them for import into Linear using CSV format.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Purpose

This tool helps you migrate from YouTrack to Linear as your issue tracking system by:
1. **Exporting issues** from YouTrack using their REST API
2. **Transforming data** to Linear-compatible CSV format
3. **Importing CSV files** using Linear's official import CLI tool

## Quick Start

### 1. Setup

```bash
# Clone and setup
git clone https://github.com/source-ag/youtrack2linear.git
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

# Linear Configuration (optional)
LINEAR_DEFAULT_STATE=Backlog
```

**Note**: 
- If you don't specify a `YOUTRACK_PROJECT_KEY` in your `.env` file, you can still export issues by providing a query with the `--query` parameter.
- Set `LINEAR_DEFAULT_STATE` to avoid issues being imported into Linear's "Triage" state (which has no bulk edit mode). Common values: `Backlog`, `Todo`, `In Progress`.

### 3. Export and Transform

```bash
# Export issues from YouTrack
python migrate.py export --query "project: PROJECT_KEY"

# Transform to Linear CSV format
python transformer.py
```

**Note**: If you don't provide a `--query` parameter, the tool will export all issues from the project specified in your `YOUTRACK_PROJECT_KEY` environment variable.

### 4. Import to Linear

Run Linear's import command and follow the wizard:

```bash
linear-import
```

In the wizard:
1. Select **"Linear CSV import"**
2. Follow the prompts to select your CSV file (`output/linear_issues.csv`)
3. Map columns as needed (Title → Title, Description → Description)
4. Complete the import

## Project Structure

```
youtrack2linear/
├── README.md              # This file
├── LICENSE                # MIT License
├── requirements.txt       # Python dependencies
├── migrate.py             # YouTrack export tool
├── transformer.py         # CSV generation tool
├── youtrack_client.py     # YouTrack API client
├── config.py             # Configuration classes
├── env_template          # Environment variables template
└── output/               # Generated files
    ├── youtrack_issues.json  # Raw export from YouTrack
    └── linear_issues.csv     # CSV for Linear import
```

## Files Created

- `output/youtrack_issues.json` - Raw export from YouTrack
- `output/linear_issues.csv` - CSV for Linear import (title and description only)

## Commands

```bash
# Test connections
python migrate.py test-connections

# Export from YouTrack
python migrate.py export --query "project: PROJECT_KEY"

# Transform to Linear CSV format
python transformer.py
```

## Complete Example

```bash
# 1. Test your connection
python migrate.py test-connections

# 2. Export issues (replace PROJECT_KEY with your actual project key)
python migrate.py export --query "project: MYPROJECT"

# 3. Transform to CSV
python transformer.py

# 4. Import to Linear using the CLI tool
linear-import
# Follow the wizard and select "Linear CSV import"
```

## Getting API Keys

### YouTrack Token
1. Go to YouTrack → Profile → Authentication
2. Create a "Permanent Token"
3. Copy the token

### Linear Import
No API key needed! The CSV import uses Linear's official CLI tool:
1. Install: `npm install --global @linear/import`
2. Run: `linear-import`
3. Follow the wizard and select **"Linear CSV import"**
4. Select your CSV file and complete the import

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
| *(configured)* | `State` | Set via `LINEAR_DEFAULT_STATE` (e.g., `backlog`) |
| *(empty)* | `Labels` | Empty for simple import |

**Note**: 
- This approach focuses on importing just the essential issue information (title and description) while maintaining compatibility with Linear's import format.
- The `State` column is populated with your configured `LINEAR_DEFAULT_STATE` to avoid issues being imported into Linear's "Triage" state.

## Query Examples

```bash
# All issues in a project
python migrate.py export --query "project: PROJECT_KEY"

# Open issues only
python migrate.py export --query "project: PROJECT_KEY State: Open"

# Issues from last month
python migrate.py export --query "project: PROJECT_KEY created: -1M .. today"

# High priority issues
python migrate.py export --query "project: PROJECT_KEY Priority: Major"
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

This tool uses **Linear's official import CLI tool** (`@linear/import`) for reliability and official support. The interactive wizard makes it easy to configure the import, and it's the officially supported method from Linear.

## License

MIT License - see LICENSE file for details.