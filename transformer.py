#!/usr/bin/env python3
"""
Simple data transformer for YouTrack to Linear migration.
Only exports titles and descriptions to avoid complexity.
"""

import json
import csv
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from rich.console import Console

console = Console()


class Transformer:
    """Simple transformer that only extracts titles and descriptions."""
    
    def __init__(self):
        pass
    
    def _clean_description(self, description: Optional[str]) -> Optional[str]:
        """Clean and format description text for Linear."""
        if not description:
            return None
        
        # Remove YouTrack-specific formatting
        cleaned = description
        
        # Convert YouTrack wiki markup to Markdown
        # Bold: *text* -> **text**
        cleaned = re.sub(r'\*([^*]+)\*', r'**\1**', cleaned)
        
        # Italic: _text_ -> *text*
        cleaned = re.sub(r'_([^_]+)_', r'*\1*', cleaned)
        
        # Code blocks: {{code}} -> ```code```
        cleaned = re.sub(r'\{\{([^}]+)\}\}', r'```\n\1\n```', cleaned)
        
        # Links: [text|url] -> [text](url)
        cleaned = re.sub(r'\[([^|]+)\|([^\]]+)\]', r'[\1](\2)', cleaned)
        
        return cleaned.strip()
    
    def transform_issue(self, youtrack_issue: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Transform a single YouTrack issue to simple Linear format."""
        try:
            # Extract only title and description
            title = youtrack_issue.get('summary', '').strip()
            description = self._clean_description(youtrack_issue.get('description'))
            
            if not title:
                console.print(f"⚠️  Skipping issue with no title: {youtrack_issue.get('idReadable', 'unknown')}")
                return None
            
            return {
                'title': title,
                'description': description or ''
            }
            
        except Exception as e:
            issue_id = youtrack_issue.get('idReadable', 'unknown')
            console.print(f"❌ Error transforming issue {issue_id}: {e}")
            return None
    
    def transform_issues(self, youtrack_issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform multiple YouTrack issues to simple Linear format."""
        console.print(f"🔄 Transforming {len(youtrack_issues)} issues...")
        
        linear_issues = []
        skipped = 0
        
        for issue in youtrack_issues:
            transformed = self.transform_issue(issue)
            if transformed:
                linear_issues.append(transformed)
            else:
                skipped += 1
        
        console.print(f"✅ Transformed {len(linear_issues)} issues, skipped {skipped}")
        return linear_issues
    
    def save_to_csv(self, linear_issues: List[Dict[str, Any]], output_file: str):
        """Save issues to CSV format for Linear import."""
        console.print(f"💾 Saving {len(linear_issues)} issues to {output_file}")
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'Title',
                'Description', 
                'Created At',
                'Updated At',
                'Identifier',
                'Creator Email',
                'Assignee Email',
                'Priority',
                'State',
                'Labels'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for issue in linear_issues:
                # Only populate Title and Description, leave other columns empty
                row = {
                    'Title': issue.get('title', ''),
                    'Description': issue.get('description', ''),
                    'Created At': '',  # Empty for simple import
                    'Updated At': '',  # Empty for simple import
                    'Identifier': '',  # Empty for simple import
                    'Creator Email': '',  # Empty for simple import
                    'Assignee Email': '',  # Empty for simple import
                    'Priority': '',  # Empty for simple import
                    'State': '',  # Empty for simple import
                    'Labels': ''  # Empty for simple import
                }
                writer.writerow(row)
        
        console.print(f"✅ Saved to {output_file}")


def main():
    """Main function to transform YouTrack issues to Linear format."""
    # Input and output files
    input_file = 'output/youtrack_issues.json'
    output_file = 'output/linear_issues.csv'
    
    # Check input file exists
    if not Path(input_file).exists():
        console.print(f"❌ Input file not found: {input_file}")
        console.print("Run 'python migrate.py export' first to get YouTrack data")
        return
    
    # Load YouTrack issues
    console.print(f"📥 Loading issues from {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        youtrack_issues = json.load(f)
    
    console.print(f"📊 Loaded {len(youtrack_issues)} issues from YouTrack")
    
    # Transform issues
    transformer = Transformer()
    linear_issues = transformer.transform_issues(youtrack_issues)
    
    # Save to CSV
    transformer.save_to_csv(linear_issues, output_file)
    
    console.print(f"\n🎉 Transformation complete!")
    console.print(f"📁 Output file: {output_file}")
    console.print(f"📊 Issues ready for import: {len(linear_issues)}")
    console.print(f"\n📋 Next steps:")
    console.print(f"1. Go to Linear → Settings → Import Export")
    console.print(f"2. Upload {output_file}")
    console.print(f"3. Map columns: Title → Title, Description → Description")
    console.print(f"4. Import!")


if __name__ == '__main__':
    main()

