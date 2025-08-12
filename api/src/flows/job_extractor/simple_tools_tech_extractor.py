import json
from typing import Any

from flows.simple_extractor import SimpleExtractorWorkflow


TOOLS_TECH_EXTRACTOR_SYSTEM_PROMPT = """
From the given job description, extract:

Tools: the tools or software explicitly mentioned
Tech: the technologies or programming languages explicitly mentioned

Return only valid JSON in this exact schema:

{
  "tools": string[]
  "tech": string[]
}
"""

TOOLS_TECH_EXTRACTOR_PROMPT = """
{job_description}
"""


def get_tools_tech_extraction_system_prompt() -> str:
    return TOOLS_TECH_EXTRACTOR_SYSTEM_PROMPT


def get_tools_tech_extraction_prompt(job_description: str) -> str:
    return TOOLS_TECH_EXTRACTOR_PROMPT.format(job_description=job_description)


def validate_tools_tech_output(output: str) -> dict[str, Any]:
    """Validate and parse the LLM output for tools and tech extraction."""
    try:
        parsed = json.loads(output)
        if not isinstance(parsed, dict):
            raise ValueError("Output is not a dictionary")

        if "tools" not in parsed or "tech" not in parsed:
            raise ValueError("Missing required fields: tools or tech")

        if not isinstance(parsed["tools"], list):
            raise ValueError("tools must be a list")

        if not isinstance(parsed["tech"], list):
            raise ValueError("tech must be a list")

        # Remove duplicates from tools while preserving order
        seen = set()
        unique_tools = []
        for tool in parsed["tools"]:
            if isinstance(tool, str) and tool not in seen:
                seen.add(tool)
                unique_tools.append(tool)

        parsed["tools"] = unique_tools

        # Remove duplicates from tech while preserving order
        seen = set()
        unique_tech = []
        for tech in parsed["tech"]:
            if isinstance(tech, str) and tech not in seen:
                seen.add(tech)
                unique_tech.append(tech)

        parsed["tech"] = unique_tech
        return parsed

    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format")
    except Exception as e:
        raise ValueError(f"Validation error: {str(e)}")


def create_tools_tech_extractor():
    """Factory function to create a ToolsTechExtractor using SimpleExtractorWorkflow."""
    return SimpleExtractorWorkflow(
        system_prompt_func=get_tools_tech_extraction_system_prompt,
        user_prompt_func=get_tools_tech_extraction_prompt,
        validator_func=validate_tools_tech_output,
        fallback_result={"tools": [], "tech": []},
        result_key="tools_tech"
    )