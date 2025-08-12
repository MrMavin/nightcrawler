import json
from typing import Any


def validate_roles_output(output: str) -> dict[str, Any]:
    """Validate and parse the LLM output for roles extraction."""
    try:
        parsed = json.loads(output)
        if not isinstance(parsed, dict):
            raise ValueError("Output is not a dictionary")

        if "main_role" not in parsed or "related_roles" not in parsed:
            raise ValueError("Missing required fields: main_role or related_roles")

        if not isinstance(parsed["main_role"], str):
            raise ValueError("main_role must be a string")

        if not isinstance(parsed["related_roles"], list):
            raise ValueError("related_roles must be a list")

        # Remove duplicates from related_roles while preserving order
        seen = set()
        unique_roles = []
        for role in parsed["related_roles"]:
            if isinstance(role, str) and role not in seen:
                seen.add(role)
                unique_roles.append(role)

        parsed["related_roles"] = unique_roles
        return parsed

    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format")
    except Exception as e:
        raise ValueError(f"Validation error: {str(e)}")
