import json
from typing import Any

from flows.simple_extractor import SimpleExtractorWorkflow


ROLES_EXTRACTOR_SYSTEM_PROMPT = """
From the given job description, extract:

Main role: the job being hired for
Related roles: titles or variants explicit mentioned

Return only valid JSON in this exact schema:

{
  "main_role": string
  "related_roles": string[]
}
"""

ROLES_EXTRACTOR_PROMPT = """
{job_description}
"""


def get_roles_extraction_system_prompt() -> str:
    return ROLES_EXTRACTOR_SYSTEM_PROMPT


def get_roles_extraction_prompt(job_description: str) -> str:
    return ROLES_EXTRACTOR_PROMPT.format(job_description=job_description)


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


def create_roles_extractor():
    """Factory function to create a RolesExtractor using SimpleExtractorWorkflow."""
    return SimpleExtractorWorkflow(
        system_prompt_func=get_roles_extraction_system_prompt,
        user_prompt_func=get_roles_extraction_prompt,
        validator_func=validate_roles_output,
        fallback_result={"main_role": "Unknown", "related_roles": []},
        result_key="roles"
    )