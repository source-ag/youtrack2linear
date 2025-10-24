"""Configuration settings for YouTrack to Linear migration."""

import os
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class YouTrackConfig(BaseModel):
    """YouTrack API configuration."""
    base_url: str = Field(..., description="YouTrack instance URL (e.g., https://your-instance.myjetbrains.com/youtrack)")
    api_token: str = Field(..., description="YouTrack permanent API token")
    project_key: Optional[str] = Field(None, description="Project key to filter issues (optional)")
    batch_size: int = Field(100, description="Number of issues to fetch per API call")
    
    @validator('base_url')
    def validate_base_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('base_url must start with http:// or https://')
        return v.rstrip('/')


class LinearConfig(BaseModel):
    """Linear configuration."""
    team_key: str = Field(..., description="Linear team key to import issues into")
    default_state: Optional[str] = Field(None, description="Default state for imported issues (e.g., 'backlog', 'todo')")


class MigrationConfig(BaseModel):
    """Migration settings."""
    output_dir: str = Field("./output", description="Directory to store exported data")
    max_retries: int = Field(3, description="Maximum number of retries for API calls")
    retry_delay: float = Field(1.0, description="Initial delay between retries (seconds)")
    field_mapping: Dict[str, str] = Field(
        default_factory=lambda: {
            'summary': 'title',
            'description': 'description',
            'created': 'createdAt',
            'updated': 'updatedAt',
            'idReadable': 'identifier',
        },
        description="Mapping of YouTrack fields to Linear fields"
    )
    
    # YouTrack fields to fetch
    youtrack_fields: str = Field(
        "idReadable,summary,description,created,updated,resolved,reporter(name,email),"
        "assignee(name,email),priority(name),state(name),tags(name),customFields(name,value)",
        description="YouTrack API fields to fetch"
    )


class Config(BaseModel):
    """Main configuration."""
    youtrack: YouTrackConfig
    linear: LinearConfig
    migration: MigrationConfig = Field(default_factory=MigrationConfig)
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Create configuration from environment variables."""
        return cls(
            youtrack=YouTrackConfig(
                base_url=os.getenv('YOUTRACK_URL', ''),
                api_token=os.getenv('YOUTRACK_TOKEN', ''),
                project_key=os.getenv('YOUTRACK_PROJECT_KEY'),
                batch_size=int(os.getenv('YOUTRACK_BATCH_SIZE', '100'))
            ),
            linear=LinearConfig(
                team_key=os.getenv('LINEAR_TEAM_KEY', ''),
                default_state=os.getenv('LINEAR_DEFAULT_STATE')
            ),
            migration=MigrationConfig(
                output_dir=os.getenv('OUTPUT_DIR', './output'),
                max_retries=int(os.getenv('MAX_RETRIES', '3')),
                retry_delay=float(os.getenv('RETRY_DELAY', '1.0'))
            )
        )
