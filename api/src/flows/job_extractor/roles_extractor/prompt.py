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
