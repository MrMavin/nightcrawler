import json
from typing import Any

from flows.simple_extractor import SimpleExtractorWorkflow


class ValidationError(Exception):
    """Custom validation error with separate Python and LLM messages."""

    def __init__(self, python_message: str, llm_guidance: str):
        self.python_message = python_message
        self.llm_guidance = llm_guidance
        super().__init__(python_message)


EXTRACT_PROPERTIES_SYSTEM_PROMPT = """
You are a partial CV content extractor with the goal to create exact key value pairs.

KEY that is a compact, lower_snake_case field name that you would find in a CV (e.g. name, contact, location, job_title, experience, education, skills, certifications, languages, projects, publications, preferences, portfolio, linkedin, github),

VALUE is a relevant field summary as a string.

Output a JSON object with this exact format:

{"key": "string"}
"""

EXTRACT_PROPERTIES_PROMPT = """
{validation_errors}

{chunk}
"""


def get_extract_properties_system_prompt() -> str:
    return EXTRACT_PROPERTIES_SYSTEM_PROMPT


def get_extract_properties_prompt(chunk: str, validation_errors: str = "") -> str:
    errors_section = validation_errors if validation_errors.strip() else ""
    return EXTRACT_PROPERTIES_PROMPT.format(chunk=chunk, validation_errors=errors_section)


def validate_extract_properties_output(output: str) -> dict[str, str]:
    """Validate and parse the LLM output for extract properties."""
    errors = []

    try:
        # Remove JSON code block markers if present
        cleaned_output = output.strip()
        if cleaned_output.startswith("```json"):
            cleaned_output = cleaned_output[7:]
        if cleaned_output.endswith("```"):
            cleaned_output = cleaned_output[:-3]
        cleaned_output = cleaned_output.strip()

        parsed = json.loads(cleaned_output)
        if not isinstance(parsed, dict):
            errors.append(
                "Your output must be a JSON dictionary/object with key-value pairs.")
        else:
            validated_properties = {}

            for key, value in parsed.items():
                if not isinstance(key, str):
                    errors.append(
                        f"Key '{key}' is not a string. All keys must be strings.")

                    continue

                if isinstance(value, (dict, list)):
                    errors.append(
                        f"Value for key '{key}' is a complex object. Only simple string values are allowed, no nested objects or arrays.")

                    continue

                validated_properties[key] = str(value)

            if not errors:
                return validated_properties

    except json.JSONDecodeError:
        errors.append(
            "Your output must be valid JSON. Do not wrap JSON in code blocks.")

    if errors:
        python_message = f"Validation failed with {len(errors)} errors"
        llm_guidance = "\n".join(f"- {error}" for error in errors)
        raise ValidationError(python_message, llm_guidance)


def create_extract_properties_workflow():
    """Factory function to create a ExtractPropertiesExtractor using SimpleExtractorWorkflow."""
    return SimpleExtractorWorkflow(
        system_prompt_func=get_extract_properties_system_prompt,
        user_prompt_func=get_extract_properties_prompt,
        validator_func=validate_extract_properties_output,
        fallback_result={},
        result_key="properties"
    )
