"""Main application module."""

import asyncio
from pathlib import Path

import llama_index.core
from dotenv import load_dotenv

from flows.job_extractor.simple_roles_extractor import create_roles_extractor
from flows.job_extractor.simple_tools_tech_extractor import create_tools_tech_extractor
from flows.job_extractor.simple_heavy_constraints_extractor import create_heavy_constraints_extractor
from logger import get_logger
from utils.cache import is_extraction_cached, get_cached_extraction, save_extraction_result

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

    # Define workflows to run
    workflows = [
        ("RolesExtractorWorkflow", create_roles_extractor),
        ("ToolsTechExtractorWorkflow", create_tools_tech_extractor),
        ("HeavyConstraintsExtractorWorkflow", create_heavy_constraints_extractor),
    ]

    # Process each job file
    for job_file in txt_files:
        log.info(f"Processing job file: {job_file.name}")

        # Read the job content
        job_content = job_file.read_text()
        log.debug(f"Job content length: {len(job_content)} characters")

        # Check which workflows need to be run (not cached)
        workflows_to_run = []
        cached_results = {}

        for workflow_name, workflow_factory in workflows:
            if is_extraction_cached(job_file, workflow_name):
                log.info(
                    f"Found cached result for {job_file.name} - {workflow_name}")
                cached_results[workflow_name] = get_cached_extraction(
                    job_file, workflow_name)
            else:
                log.info(
                    f"No cache found for {job_file.name} - {workflow_name}, adding to execution queue")
                workflows_to_run.append((workflow_name, workflow_factory))

        # Run workflows in parallel if needed
        if workflows_to_run:
            log.info(
                f"Running {len(workflows_to_run)} workflows in parallel for {job_file.name}")

            async def run_workflow(workflow_name, workflow_factory):
                w = workflow_factory()
                result = await w.run(job_description=job_content)
                save_extraction_result(job_file, workflow_name, result)
                return workflow_name, result

            # Execute workflows in parallel
            tasks = [run_workflow(name, factory) for name, factory in workflows_to_run]
            results = await asyncio.gather(*tasks)

            # Add new results to cached results
            for workflow_name, result in results:
                cached_results[workflow_name] = result

        log.info(f"Completed processing {job_file.name}")
        print(f"\n--- Results for {job_file.name} ---")
        for workflow_name, result in cached_results.items():
            print(f"\n{workflow_name}:")
            print(result)
        print("---" * 20)

    log.info("All job files processed")


if __name__ == "__main__":
    asyncio.run(main())
