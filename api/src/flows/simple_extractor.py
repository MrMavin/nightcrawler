import json
from typing import Callable, Any, Optional
import inspect

from llama_index.core.llms import ChatMessage
from llama_index.core.workflow import (
    StartEvent,
    StopEvent,
    Workflow,
    step,
    Event,
)
from llama_index.llms.groq import Groq

from logger import get_logger
from settings import settings
from utils.retry import async_retry
from utils.text_cleaner import normalize_text, remove_all_emojis

log = get_logger(__name__)


class SimpleExtractorEvent(Event):
    result: str


class SimpleExtractorWorkflow(Workflow):
    def __init__(
        self,
        system_prompt_func: Callable[[], str],
        user_prompt_func: Callable[[str], str],
        validator_func: Callable[[str], dict],
        fallback_result: dict,
        result_key: str,
        llm_model: str = "openai/gpt-oss-120b"
    ):
        super().__init__()
        self.system_prompt_func = system_prompt_func
        self.user_prompt_func = user_prompt_func
        self.validator_func = validator_func
        self.fallback_result = fallback_result
        self.result_key = result_key
        self.llm = Groq(model=llm_model, api_key=settings.groq_api_key)

    def _clean_job_description(self, job_description: str) -> str:
        """Clean job description by removing emojis and normalizing text."""
        cleaned = remove_all_emojis(job_description)
        cleaned = normalize_text(cleaned)
        return cleaned

    @async_retry(max_retries=3, exceptions=Exception)
    async def _extract_data(self, job_description: str, validation_errors: str = "") -> dict:
        """Extract data using provided prompts and validator."""
        # Check if user_prompt_func accepts validation_errors parameter
        sig = inspect.signature(self.user_prompt_func)
        if 'validation_errors' in sig.parameters:
            user_prompt = self.user_prompt_func(
                job_description, f"Follow these instructions:\n{validation_errors}")
        else:
            user_prompt = self.user_prompt_func(job_description)

        response = self.llm.chat(
            messages=[
                ChatMessage(
                    role="system", content=self.system_prompt_func()
                ),
                ChatMessage(
                    role="user", content=user_prompt
                ),
            ],
            timeout=60,
            temperature=0,
        )

        log.debug(f"Raw LLM response: {response}")

        # Validate and parse the output
        validated_output = self.validator_func(str(response.message.content))
        log.info(
            f"Successfully extracted and validated data: {validated_output}")
        return validated_output

    @step
    async def extract(self, ev: StartEvent) -> SimpleExtractorEvent:
        job_description = ev.job_description

        # Clean the job description
        cleaned_description = self._clean_job_description(job_description)
        log.debug(f"Cleaned job description: {cleaned_description[:50]}...")

        validation_errors = ""
        max_attempts = 3

        for attempt in range(max_attempts):
            try:
                validated_output = await self._extract_data(cleaned_description, validation_errors)

                return SimpleExtractorEvent(result=json.dumps(validated_output))
            except Exception as e:
                if hasattr(e, 'llm_guidance') and attempt < max_attempts - 1:
                    validation_errors = e.llm_guidance
                    log.warning(
                        f"Validation error on attempt {attempt + 1}: {e.python_message}")
                    continue
                else:
                    log.error(
                        f"Failed to extract data after {attempt + 1} attempts: {str(e)}")
                    return SimpleExtractorEvent(result=json.dumps(self.fallback_result))

    @step
    async def return_data(self, ev: SimpleExtractorEvent) -> StopEvent:
        return StopEvent(result=str(ev.result))
