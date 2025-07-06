#!/bin/bash

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOL
NOTION_TOKEN=your_notion_token
NOTION_VERSION=2022-06-28

# Database IDs
SOCIAL_MEDIA_DB=your_social_media_db_id
TEAM_DB=your_team_db_id
KPI_DB=your_kpi_db_id
TASKS_DB=your_tasks_db_id
EOL
    echo ".env file created. Please update it with your actual values."
fi

# Create necessary directories
mkdir -p src/services/notion
mkdir -p src/models
mkdir -p src/config
mkdir -p tests/notion

echo "Setup completed successfully!" 