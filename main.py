import click
from config.database_config import init_database
from services.sync_service import SyncService
from services.notion_client import NotionClient

@click.group()
def cli():
    """Notion Data Management CLI"""
    pass

@cli.command()
@click.argument('database_type')
def sync(database_type):
    """Synchronize data from Notion to local database"""
    try:
        sync_service = SyncService()
        count = sync_service.sync_database(database_type)
        click.echo(f"Successfully synchronized {count} records from {database_type}")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
    finally:
        sync_service.close()

@cli.command()
@click.argument('database_type')
@click.option('--title', help='Filter by title')
@click.option('--status', help='Filter by status')
def query(database_type, title, status):
    """Query local database"""
    try:
        import sqlite3
        from config.database_config import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = f"SELECT * FROM {database_type} WHERE 1=1"
        params = []
        
        if title:
            query += " AND title LIKE ?"
            params.append(f"%{title}%")
        
        if status:
            query += " AND status = ?"
            params.append(status)
            
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        for row in results:
            click.echo(dict(row))
            
    except sqlite3.Error as e:
        click.echo(f"Database error: {str(e)}", err=True)
    finally:
        conn.close()

@cli.command()
def init_db():
    """Initialize the local database"""
    try:
        init_database()
        click.echo("Database initialized successfully")
    except Exception as e:
        click.echo(f"Error initializing database: {str(e)}", err=True)

@cli.command()
@click.argument('database_type')
@click.option('--title', required=True, help='Title of the new item')
@click.option('--status', help='Status of the item')
def create(database_type, title, status):
    """Create a new item in Notion database"""
    try:
        notion = NotionClient()
        properties = {
            "Title": {"title": [{"text": {"content": title}}]},
        }
        
        if status:
            properties["Status"] = {"select": {"name": status}}
            
        database_id = notion.NOTION_DATABASE_IDS.get(database_type)
        if not database_id:
            raise ValueError(f"Unknown database type: {database_type}")
            
        result = notion.create_page(database_id, properties)
        click.echo(f"Successfully created new {database_type} item with ID: {result['id']}")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)

if __name__ == '__main__':
    cli() 