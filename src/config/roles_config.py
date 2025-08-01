# roles_config.py
"""Role mapping for Telegram bots.

Add Telegram user IDs and assign roles. Roles: executive, manager, performer, guest.
"""
from typing import Dict

# Map telegram user_id to role name
USER_ROLES: Dict[int, str] = {
    # Example IDs – replace with real
    123456789: "executive",
    987654321: "manager",
    112233445: "performer",
}

# Role-specific allowed commands
ROLE_COMMANDS: Dict[str, list[str]] = {
    "executive": [
        "start",
        "summary",
        "export_excel",
        "create_task",
    ],
    "manager": [
        "start",
        "tasks",
        "export_excel",
    ],
    "performer": [
        "start",
        "my_tasks",
    ],
    "guest": [
        "start",
    ],
}

DEFAULT_ROLE = "guest"


def get_role(user_id: int) -> str:
    """Return role for telegram user id."""
    return USER_ROLES.get(user_id, DEFAULT_ROLE)


def is_command_allowed(role: str, command: str) -> bool:
    """Check if command is allowed for role."""
    return command in ROLE_COMMANDS.get(role, []) 