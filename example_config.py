"""
Example configuration file for YouTrack to Linear migration.

Copy this file to config_local.py and customize for your environment.
"""

from config import Config, YouTrackConfig, LinearConfig, MigrationConfig

# Example configuration
EXAMPLE_CONFIG = Config(
    youtrack=YouTrackConfig(
        base_url="https://your-company.myjetbrains.com/youtrack",
        api_token="your_youtrack_permanent_token_here",
        project_key="PROJ",  # Optional: filter to specific project
        batch_size=100
    ),
    linear=LinearConfig(
        team_key="DEV"  # Your Linear team key
    ),
    migration=MigrationConfig(
        output_dir="./migration_output",
        max_retries=3,
        retry_delay=1.0,
        
        # Custom field mapping (YouTrack field -> Linear field)
        field_mapping={
            'summary': 'title',
            'description': 'description', 
            'created': 'createdAt',
            'updated': 'updatedAt',
            'idReadable': 'identifier',
            # Add custom fields here
            # 'customFieldName': 'linearFieldName',
        },
        
        # YouTrack fields to fetch (customize based on your needs)
        youtrack_fields=(
            "idReadable,summary,description,created,updated,resolved,"
            "reporter(name,email,login),assignee(name,email,login),"
            "priority(name),state(name),tags(name),"
            "customFields(name,value(name,id,login,email))"
        )
    )
)

# Advanced configuration examples

# Configuration for specific use cases
MINIMAL_CONFIG = Config(
    youtrack=YouTrackConfig(
        base_url="https://your-company.myjetbrains.com/youtrack",
        api_token="your_token",
        batch_size=50  # Smaller batches for slower connections
    ),
    linear=LinearConfig(
        team_key="DEV",
        dry_run=True  # Always dry run first
    )
)

LARGE_MIGRATION_CONFIG = Config(
    youtrack=YouTrackConfig(
        base_url="https://your-company.myjetbrains.com/youtrack",
        api_token="your_token",
        batch_size=200  # Larger batches for better performance
    ),
    linear=LinearConfig(
        team_key="DEV"
    ),
    migration=MigrationConfig(
        max_retries=5,  # More retries for large migrations
        retry_delay=2.0,  # Longer delay between retries
        output_dir="./large_migration"
    )
)

# Custom priority mapping example
CUSTOM_PRIORITY_MAPPING = {
    'Critical': 1,    # Urgent
    'High': 1,        # Urgent  
    'Major': 2,       # High
    'Normal': 3,      # Medium
    'Low': 4,         # Low
    'Minor': 4,       # Low
    'Trivial': 4,     # Low
}

# Custom state mapping example  
CUSTOM_STATE_MAPPING = {
    'Open': 'backlog',
    'New': 'backlog',
    'To Do': 'backlog',
    'In Progress': 'started',
    'In Review': 'started',
    'Testing': 'started',
    'Done': 'completed',
    'Resolved': 'completed',
    'Closed': 'completed',
    'Verified': 'completed',
    'Cancelled': 'cancelled',
    'Won\'t Fix': 'cancelled',
}

# Example query filters for different migration scenarios
EXAMPLE_QUERIES = {
    # All open issues
    'open_issues': 'State: Open',
    
    # Issues from last year
    'recent_issues': 'created: -1y .. today',
    
    # High priority bugs
    'critical_bugs': 'Priority: {Critical, Major} Type: Bug',
    
    # Specific assignee
    'user_issues': 'Assignee: john.doe',
    
    # Multiple projects
    'multi_project': 'project: {PROJ1, PROJ2}',
    
    # Complex filter
    'complex': 'project: PROJ State: {Open, "In Progress"} Priority: {Critical, Major} created: -6M .. today',
}

# Field mapping for organizations with custom fields
CUSTOM_FIELD_MAPPING = {
    # Standard fields
    'summary': 'title',
    'description': 'description',
    'created': 'createdAt', 
    'updated': 'updatedAt',
    'idReadable': 'identifier',
    
    # Custom field examples (adjust based on your YouTrack setup)
    # 'Story Points': 'storyPoints',
    # 'Epic Link': 'epicId',  
    # 'Sprint': 'sprintId',
    # 'Component': 'component',
    # 'Version': 'version',
}

if __name__ == "__main__":
    print("Example configurations for YouTrack to Linear migration")
    print("Copy the relevant configuration to your .env file or config_local.py")
    print(f"Example YouTrack URL: {EXAMPLE_CONFIG.youtrack.base_url}")
    print(f"Example Linear team: {EXAMPLE_CONFIG.linear.team_key}")
    print(f"Batch size: {EXAMPLE_CONFIG.youtrack.batch_size}")
    print(f"Output directory: {EXAMPLE_CONFIG.migration.output_dir}")
