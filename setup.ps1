# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt

# Create .env file if it doesn't exist
if (-not (Test-Path .env)) {
    Write-Host "Creating .env file..."
    @"
NOTION_TOKEN=your_notion_token
NOTION_VERSION=2022-06-28

# Database IDs
SOCIAL_MEDIA_DB=your_social_media_db_id
TEAM_DB=your_team_db_id
KPI_DB=your_kpi_db_id
TASKS_DB=your_tasks_db_id
"@ | Out-File -FilePath .env -Encoding UTF8
    Write-Host ".env file created. Please update it with your actual values."
}

# Create necessary directories
New-Item -ItemType Directory -Force -Path src/services/notion
New-Item -ItemType Directory -Force -Path src/models
New-Item -ItemType Directory -Force -Path src/config
New-Item -ItemType Directory -Force -Path tests/notion

Write-Host "Setup completed successfully!" 