import json
from typing import Any

from flows.simple_extractor import SimpleExtractorWorkflow


HEAVY_CONSTRAINTS_EXTRACTOR_SYSTEM_PROMPT = """
From the given job description, extract heavy constraints.

Heavy constraints are:
- Explicit relocation
- Explicit place to work
- Explicit hybrid or in-office
- Explicit contract type that is not contract or full-time
- Explicit travel requirements
- Explicit language requirements
- Anything explicitly marked as important or not negotiable

Include mentioned elements in a list, output a valid JSON in this exact schema:

{
  "heavy_constraints": string[]
}
"""

HEAVY_CONSTRAINTS_EXTRACTOR_PROMPT = """
{job_description}
"""


def get_heavy_constraints_extraction_system_prompt() -> str:
    return HEAVY_CONSTRAINTS_EXTRACTOR_SYSTEM_PROMPT


def get_heavy_constraints_extraction_prompt(job_description: str) -> str:
    return HEAVY_CONSTRAINTS_EXTRACTOR_PROMPT.format(job_description=job_description)


def validate_heavy_constraints_output(output: str) -> dict[str, Any]:
    """Validate and parse the LLM output for heavy constraints extraction."""
    try:
        parsed = json.loads(output)
        if not isinstance(parsed, dict):
            raise ValueError("Output is not a dictionary")

        if "heavy_constraints" not in parsed:
            raise ValueError("Missing required fields: heavy_constraints")

        if not isinstance(parsed["heavy_constraints"], list):
            raise ValueError("heavy_constraints must be a list")

        # Remove duplicates from heavy_constraints while preserving order
        seen = set()
        unique_heavy_constraints = []
        for heavy_constraint in parsed["heavy_constraints"]:
            if isinstance(heavy_constraint, str) and heavy_constraint not in seen:
                seen.add(heavy_constraint)
                unique_heavy_constraints.append(heavy_constraint)

        parsed["heavy_constraints"] = unique_heavy_constraints

        return parsed

    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format")
    except Exception as e:
        raise ValueError(f"Validation error: {str(e)}")


def create_heavy_constraints_extractor():
    """Factory function to create a HeavyConstraintsExtractor using SimpleExtractorWorkflow."""
    return SimpleExtractorWorkflow(
        system_prompt_func=get_heavy_constraints_extraction_system_prompt,
        user_prompt_func=get_heavy_constraints_extraction_prompt,
        validator_func=validate_heavy_constraints_output,
        fallback_result={"heavy_constraints": []},
        result_key="heavy_constraints"
    )