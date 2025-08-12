"""Main application module."""

import asyncio
from pathlib import Path

import llama_index.core
from dotenv import load_dotenv

from flows.job_extractor.roles_extractor.workflow import RolesExtractorWorkflow
from logger import get_logger

log = get_logger(__name__)

llama_index.core.set_global_handler("arize_phoenix")


async def main():
    """Main entry point."""
    load_dotenv()

    log.info("Starting Nightcrawler API")

    # Get all txt files from data/jobs directory
    jobs_dir = Path("data/jobs")
    txt_files = list(jobs_dir.glob("*.txt"))

    log.info(f"Found {len(txt_files)} job files to process")

    # Process each job file
    for job_file in txt_files:
        log.info(f"Processing job file: {job_file.name}")

        # Read the job content
        job_content = job_file.read_text()
        log.debug(f"Job content length: {len(job_content)} characters")

        # Run workflow with job content as topic
        w = RolesExtractorWorkflow(timeout=60, verbose=True)
        result = await w.run(job_description=job_content)

        log.info(f"Completed processing {job_file.name}")
        print(f"\n--- Results for {job_file.name} ---")
        print(result)
        print("---" * 20)

    log.info("All job files processed")


if __name__ == "__main__":
    asyncio.run(main())
