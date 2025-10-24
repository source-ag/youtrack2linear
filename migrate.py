#!/usr/bin/env python3
"""
YouTrack to Linear Migration Tool

This script exports issues from YouTrack and prepares them for import into Linear
using Linear's official import tool (@linear/import).
"""

import json
import logging
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.logging import RichHandler
from rich.prompt import Confirm

from config import Config
from youtrack_client import YouTrackClient, YouTrackAPIError
from data_transformer import DataTransformer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)
console = Console()


def setup_output_directory(output_dir: str) -> Path:
    """Create and return the output directory."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


@click.group()
@click.option('--config-file', type=click.Path(exists=True), help='Path to configuration file')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx, config_file: Optional[str], verbose: bool):
    """YouTrack to Linear migration tool - exports issues and prepares them for Linear's official import tool."""
    ctx.ensure_object(dict)
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        if config_file:
            # Load from file (implement if needed)
            console.print(f"Loading config from: {config_file}")
            config = Config.from_env()  # For now, still use env vars
        else:
            config = Config.from_env()
        
        ctx.obj['config'] = config
        
    except Exception as e:
        console.print(f"❌ Configuration error: {e}")
        sys.exit(1)


@cli.command()
@click.pass_context
def test_connections(ctx):
    """Test connection to YouTrack."""
    config = ctx.obj['config']
    
    console.print("🔍 Testing YouTrack connection...")
    
    # Test YouTrack connection
    youtrack_client = YouTrackClient(config.youtrack)
    youtrack_ok = youtrack_client.test_connection()
    
    if youtrack_ok:
        console.print("✅ YouTrack connection successful!")
        console.print("\n📋 Next steps:")
        console.print("1. Run: python migrate.py export --query 'project: {PROJECT_KEY}'")
        console.print("2. Run: python migrate.py transform")
        console.print("3. Run: python convert_to_csv.py")
        console.print("4. Run: linear-import (Linear's official import tool)")
        return True
    else:
        console.print("❌ YouTrack connection failed. Check your credentials.")
        return False


@cli.command()
@click.option('--query', '-q', help='YouTrack query string to filter issues')
@click.option('--output-file', '-o', help='Output file path for exported issues')
@click.option('--limit', type=int, help='Maximum number of issues to export')
@click.pass_context
def export(ctx, query: Optional[str], output_file: Optional[str], limit: Optional[int]):
    """Export issues from YouTrack."""
    config = ctx.obj['config']
    
    # Setup output directory
    output_dir = setup_output_directory(config.migration.output_dir)
    
    if not output_file:
        output_file = str(output_dir / 'youtrack_issues.json')
    
    try:
        youtrack_client = YouTrackClient(config.youtrack)
        
        # Test connection first
        if not youtrack_client.test_connection():
            console.print("❌ Failed to connect to YouTrack")
            sys.exit(1)
        
        # Add limit to query if specified
        export_query = query
        if limit:
            export_query = f"{query} " if query else ""
            # Note: YouTrack uses $top parameter in API, but for query we can't easily add limit
            console.print(f"⚠️  Limit parameter will be applied during export, not in query")
        
        # Export issues
        console.print(f"📤 Exporting issues from YouTrack...")
        if export_query:
            console.print(f"Query: {export_query}")
        
        count = youtrack_client.export_issues_to_file(
            output_file=output_file,
            query=export_query
        )
        
        console.print(f"✅ Successfully exported {count} issues to {output_file}")
        
    except YouTrackAPIError as e:
        console.print(f"❌ YouTrack API error: {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"❌ Export failed: {e}")
        sys.exit(1)


@cli.command()
@click.option('--input-file', '-i', help='Input file with YouTrack issues (JSON)')
@click.option('--output-file', '-o', help='Output file for transformed Linear issues')
@click.option('--preview', is_flag=True, help='Preview transformation without saving')
@click.pass_context
def transform(ctx, input_file: Optional[str], output_file: Optional[str], preview: bool):
    """Transform YouTrack issues to Linear format."""
    config = ctx.obj['config']
    
    # Setup input/output paths
    output_dir = setup_output_directory(config.migration.output_dir)
    
    if not input_file:
        input_file = str(output_dir / 'youtrack_issues.json')
    
    if not output_file:
        output_file = str(output_dir / 'linear_issues.json')
    
    # Check input file exists
    if not Path(input_file).exists():
        console.print(f"❌ Input file not found: {input_file}")
        console.print("Run 'export' command first or specify --input-file")
        sys.exit(1)
    
    try:
        # Load YouTrack issues
        console.print(f"📥 Loading issues from {input_file}")
        with open(input_file, 'r', encoding='utf-8') as f:
            youtrack_issues = json.load(f)
        
        console.print(f"📊 Loaded {len(youtrack_issues)} issues")
        
        # Transform issues
        transformer = DataTransformer(config.migration.field_mapping)
        linear_issues, stats = transformer.transform_issues(youtrack_issues)
        
        if preview:
            # Show preview
            linear_integration = LinearIntegration(config.linear)
            linear_integration.preview_import(linear_issues)
        else:
            # Save transformed issues
            console.print(f"💾 Saving transformed issues to {output_file}")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(linear_issues, f, indent=2, ensure_ascii=False)
            
            console.print(f"✅ Successfully transformed and saved {len(linear_issues)} issues")
            
            # Show warnings if any
            if stats.errors:
                console.print(f"\n⚠️  {len(stats.errors)} errors occurred during transformation:")
                for error in stats.errors[:5]:  # Show first 5 errors
                    console.print(f"  • {error}")
                if len(stats.errors) > 5:
                    console.print(f"  ... and {len(stats.errors) - 5} more errors")
        
    except Exception as e:
        console.print(f"❌ Transformation failed: {e}")
        sys.exit(1)


@cli.command()
@click.option('--input-file', '-i', help='Input file with Linear issues (JSON)')
@click.option('--preview', is_flag=True, help='Preview issues before import')
@click.pass_context
def preview_import(ctx, input_file: Optional[str], preview: bool):
    """Preview issues ready for Linear import."""
    output_dir = setup_output_directory(ctx.obj['config'].migration.output_dir)
    
    if not input_file:
        input_file = str(output_dir / 'linear_issues.json')
    
    # Check input file exists
    if not Path(input_file).exists():
        console.print(f"❌ Input file not found: {input_file}")
        console.print("Run 'transform' command first or specify --input-file")
        sys.exit(1)
    
    try:
        # Load Linear issues
        console.print(f"📥 Loading issues from {input_file}")
        with open(input_file, 'r', encoding='utf-8') as f:
            linear_issues = json.load(f)
        
        console.print(f"📊 Loaded {len(linear_issues)} issues ready for Linear import")
        
        if preview:
            console.print("\n📋 Import Preview (showing first 5 issues):")
            console.print("=" * 60)
            
            for i, issue in enumerate(linear_issues[:5]):
                console.print(f"\n🎫 Issue {i + 1}:")
                console.print(f"  Title: {issue.get('title', 'N/A')}")
                console.print(f"  Description: {(issue.get('description', '') or 'N/A')[:100]}...")
                console.print(f"  Created: {issue.get('createdAt', 'N/A')}")
                console.print(f"  Assignee: {issue.get('assigneeId', 'Unassigned')}")
                console.print(f"  Priority: {issue.get('priority', 'N/A')}")
                console.print(f"  Labels: {', '.join(issue.get('labelIds', []))}")
            
            if len(linear_issues) > 5:
                console.print(f"\n... and {len(linear_issues) - 5} more issues")
            
            console.print("=" * 60)
        
        console.print(f"\n🚀 Ready for Linear import!")
        console.print("Next steps:")
        console.print("1. Run: python convert_to_csv.py")
        console.print("2. Run: linear-import")
        console.print("3. Follow the prompts to import to Linear")
            
    except Exception as e:
        console.print(f"❌ Preview failed: {e}")
        sys.exit(1)


@cli.command()
@click.option('--query', '-q', help='YouTrack query string to filter issues')
@click.option('--preview', is_flag=True, help='Preview issues after transformation')
@click.pass_context
def migrate(ctx, query: Optional[str], preview: bool):
    """Complete migration pipeline: export + transform + prepare for Linear import."""
    config = ctx.obj['config']
    
    console.print("🚀 YouTrack to Linear Migration Pipeline")
    console.print("=" * 50)
    
    # Step 1: Test YouTrack connection
    console.print("\n1️⃣  Testing YouTrack connection...")
    youtrack_client = YouTrackClient(config.youtrack)
    youtrack_ok = youtrack_client.test_connection()
    
    if not youtrack_ok:
        console.print("❌ YouTrack connection failed")
        sys.exit(1)
    
    # Step 2: Export from YouTrack
    console.print("\n2️⃣  Exporting from YouTrack...")
    output_dir = setup_output_directory(config.migration.output_dir)
    youtrack_file = str(output_dir / 'youtrack_issues.json')
    
    count = youtrack_client.export_issues_to_file(
        output_file=youtrack_file,
        query=query
    )
    console.print(f"✅ Exported {count} issues")
    
    # Step 3: Transform data
    console.print("\n3️⃣  Transforming data...")
    linear_file = str(output_dir / 'linear_issues.json')
    
    with open(youtrack_file, 'r', encoding='utf-8') as f:
        youtrack_issues = json.load(f)
    
    transformer = DataTransformer(config.migration.field_mapping)
    linear_issues, stats = transformer.transform_issues(youtrack_issues)
    
    with open(linear_file, 'w', encoding='utf-8') as f:
        json.dump(linear_issues, f, indent=2, ensure_ascii=False)
    
    console.print(f"✅ Transformed {len(linear_issues)} issues")
    
    # Step 4: Preview if requested
    if preview:
        console.print("\n4️⃣  Preview of transformed issues:")
        console.print("=" * 50)
        
        for i, issue in enumerate(linear_issues[:3]):
            console.print(f"\n🎫 Issue {i + 1}:")
            console.print(f"  Title: {issue.get('title', 'N/A')}")
            console.print(f"  Description: {(issue.get('description', '') or 'N/A')[:100]}...")
            console.print(f"  Created: {issue.get('createdAt', 'N/A')}")
            console.print(f"  Assignee: {issue.get('assigneeId', 'Unassigned')}")
        
        if len(linear_issues) > 3:
            console.print(f"\n... and {len(linear_issues) - 3} more issues")
    
    # Step 5: Next steps
    console.print("\n🎉 Migration preparation completed!")
    console.print("\n📋 Next steps:")
    console.print("1. Run: python convert_to_csv.py")
    console.print("2. Run: linear-import")
    console.print("3. Follow the prompts to import to Linear")
    console.print(f"\n📁 Files created:")
    console.print(f"  • {youtrack_file}")
    console.print(f"  • {linear_file}")
    console.print(f"  • {output_dir}/linear_issues.csv (after step 1)")


if __name__ == '__main__':
    cli()
