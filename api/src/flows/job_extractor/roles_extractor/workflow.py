import json

from llama_index.core.llms import ChatMessage
from llama_index.core.workflow import (
    StartEvent,
    StopEvent,
    Workflow,
    step,
)
from llama_index.llms.groq import Groq

from logger import get_logger
from settings import settings
from utils.retry import async_retry
from utils.text_cleaner import normalize_text, remove_all_emojis

from .events import RolesExtractorEvent
from .prompt import get_roles_extraction_prompt, get_roles_extraction_system_prompt
from .validator import validate_roles_output

log = get_logger(__name__)


class RolesExtractorWorkflow(Workflow):
    llm = Groq(model="openai/gpt-oss-120b", api_key=settings.groq_api_key)

    def _clean_job_description(self, job_description: str) -> str:
        """Clean job description by removing emojis and normalizing text."""
        cleaned = remove_all_emojis(job_description)
        cleaned = normalize_text(cleaned)
        return cleaned

    @async_retry(max_retries=3, exceptions=Exception)
    async def _extract_roles(self, job_description: str) -> dict:
        """Extract roles with validation."""
        response = self.llm.chat(
            messages=[
                ChatMessage(
                    role="system", content=get_roles_extraction_system_prompt()
                ),
                ChatMessage(
                    role="user", content=get_roles_extraction_prompt(job_description)
                ),
            ],
            timeout=60,
            temperature=0,
        )

        log.debug(f"Raw LLM response: {response}")

        # Validate and parse the output
        validated_output = validate_roles_output(str(response.message.content))
        log.info(
            f"Successfully extracted and validated roles: {validated_output}")
        return validated_output

    @step
    async def roles_extractor(self, ev: StartEvent) -> RolesExtractorEvent:
        job_description = ev.job_description

        # Clean the job description
        cleaned_description = self._clean_job_description(job_description)
        log.debug(f"Cleaned job description: {cleaned_description[:50]}...")

        try:
            validated_output = await self._extract_roles(cleaned_description)
            return RolesExtractorEvent(roles=json.dumps(validated_output))
        except Exception as e:
            log.error(f"Failed to extract roles after all retries: {str(e)}")

            fallback_result = {
                "main_role": "Unknown",
                "related_roles": []
            }

            return RolesExtractorEvent(roles=json.dumps(fallback_result))

    @step
    async def return_data(self, ev: RolesExtractorEvent) -> StopEvent:
        return StopEvent(result=str(ev.roles))
