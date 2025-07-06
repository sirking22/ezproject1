import sqlite3
from pathlib import Path

# Database configuration
DB_PATH = Path(__file__).parent.parent / "data" / "notion_cache.db"
DB_PATH.parent.mkdir(exist_ok=True)

def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

# Database initialization queries
INIT_QUERIES = {
    'tasks': """
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT,
            status TEXT,
            content TEXT,
            last_edited TIMESTAMP,
            properties TEXT,
            notion_url TEXT
        )
    """,
    'projects': """
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            title TEXT,
            status TEXT,
            content TEXT,
            start_date DATE,
            end_date DATE,
            last_edited TIMESTAMP,
            properties TEXT,
            notion_url TEXT
        )
    """,
    'guides': """
        CREATE TABLE IF NOT EXISTS guides (
            id TEXT PRIMARY KEY,
            title TEXT,
            category TEXT,
            content TEXT,
            last_edited TIMESTAMP,
            properties TEXT,
            notion_url TEXT
        )
    """
}

def init_database():
    """Initialize the database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for query in INIT_QUERIES.values():
        cursor.execute(query)
    
    conn.commit()
    conn.close() 