#!/usr/bin/env python3
"""
Simple YouTrack Export Tool

This script exports issues from YouTrack for use with transformer.py
"""

import json
import logging
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.logging import RichHandler

from config import Config
from youtrack_client import YouTrackClient, YouTrackAPIError

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)
console = Console()


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx, verbose: bool):
    """Simple YouTrack export tool for Linear migration."""
    ctx.ensure_object(dict)
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
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
    
    try:
        youtrack_client = YouTrackClient(config.youtrack)
        success = youtrack_client.test_connection()
        
        if success:
            console.print("✅ YouTrack connection successful!")
        else:
            console.print("❌ YouTrack connection failed")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"❌ Connection test failed: {e}")
        sys.exit(1)


@cli.command()
@click.option('--query', '-q', help='YouTrack query string to filter issues')
@click.option('--output-file', '-o', help='Output file for YouTrack issues (JSON)')
# Limit parameter removed - not supported by YouTrackClient
@click.pass_context
def export(ctx, query: Optional[str], output_file: Optional[str]):
    """Export issues from YouTrack."""
    config = ctx.obj['config']
    
    # Setup output path
    output_dir = Path(config.migration.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not output_file:
        output_file = str(output_dir / 'youtrack_issues.json')
    
    console.print("📤 Exporting issues from YouTrack...")
    console.print(f"Query: {query or 'All issues'}")
    console.print(f"Output: {output_file}")
    
    try:
        youtrack_client = YouTrackClient(config.youtrack)
        count = youtrack_client.export_issues_to_file(
            output_file=output_file,
            query=query
        )
        
        console.print(f"✅ Exported {count} issues to {output_file}")
        console.print("\n📋 Next steps:")
        console.print("1. Run: python transformer.py")
        console.print("2. Upload output/linear_issues.csv to Linear")
        
    except Exception as e:
        console.print(f"❌ Export failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    cli()
