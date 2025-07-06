from datetime import datetime, timedelta, UTC
from typing import Optional
import pytz

def parse_notion_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse Notion date string to datetime object."""
    if not date_str:
        return None
    try:
        # Parse ISO format date from Notion
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        # Convert to UTC
        dt = dt.replace(tzinfo=UTC)
        # Convert to local timezone
        local_tz = pytz.timezone("Europe/Moscow")  # Use your local timezone
        return dt.astimezone(local_tz)
    except Exception as e:
        print(f"Error parsing date {date_str}: {e}")
        return None

def format_notion_date(date: Optional[datetime]) -> Optional[str]:
    """Format datetime object to Notion date string."""
    if not date:
        return None
    try:
        # Convert to UTC for Notion
        if date.tzinfo is None:
            # If naive datetime, assume it's in local timezone
            local_tz = pytz.timezone("Europe/Moscow")  # Use your local timezone
            date = local_tz.localize(date)
        utc_date = date.astimezone(UTC)
        return utc_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception as e:
        print(f"Error formatting date {date}: {e}")
        return None

def calculate_next_review(confidence_level: int) -> datetime:
    """Calculate next review date based on confidence level."""
    now = datetime.now(UTC)
    if confidence_level < 30:
        return now + timedelta(days=1)
    elif confidence_level < 60:
        return now + timedelta(days=3)
    elif confidence_level < 90:
        return now + timedelta(days=7)
    else:
        return now + timedelta(days=14)

def is_overdue(due_date: Optional[datetime]) -> bool:
    """Check if a task is overdue."""
    if not due_date:
        return False
    # Convert to UTC for comparison
    now = datetime.now(UTC)
    if due_date.tzinfo is None:
        # If naive datetime, assume it's in local timezone
        local_tz = pytz.timezone("Europe/Moscow")  # Use your local timezone
        due_date = local_tz.localize(due_date)
    return now > due_date.astimezone(UTC) 